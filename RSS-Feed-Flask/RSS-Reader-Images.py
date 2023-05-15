import requests
import re
import time
import feedparser
from pprint import pprint


def generalised_parse(url):
    raw = ''
    try:
        response = requests.get(url)

        if response and response.status_code == 200:
            raw = response.text

        else:
            pass

    except (requests.exceptions.ConnectionError, requests.exceptions.MissingSchema):
        pass

    # if raw <item>'s have a '<image> ... </image>' pattern extract the image url and
    # put this image url in an <enclosure /> tag which can be handled by feedparser
    raw = re.sub(r'(<item>.*?)<image>.*?(http.*?jpg|png|gif).*?</image>(.*?</item>)',
                 r'\1<enclosure url="\2" />\3', raw)
    
    # some url give an empty raw string, in that case parse with the url instead of 
    # the raw string
    if raw:
        parser = feedparser.parse(raw)

    else:
        parser = feedparser.parse(url)

    newsInfo = []
    for entry in parser.entries:
        # looks like entry has always an attribute enclosures, although maybe an 
        # empty list
        if entry.enclosures:
            enclosure_href = entry.enclosures[0]['href']
        
        else:
            enclosure_href = ''

        # check if there is media_content
        try:
            media_url = entry.media_content[0]['url']
        
        except AttributeError:
            media_url = ''

        # some entry have no attribute published, in that case check for attribute
        # updated, if that does not exist give default date of 1970-1-1
        try: 
            published = entry.published
            published_parsed = entry.updated_parsed
        
        except AttributeError:
            published = entry.get('updated', '1970-01-01')
            published_parsed = entry.get('updated_parsed', 
                time.struct_time((1970, 1, 1, 0, 0, 0, 0, 0, 0)))

        # use get method so that in case attribute does not exist we can give a default
        # value
        newEntry = {
            'title': entry.get('title', ''),
            'description': entry.get('summary', ''),
            'link': entry.get('link', ''),
            'enclosure' : enclosure_href,
            'media': media_url,
            'date': published_parsed,
            'displayDate': published,
        }
        newsInfo.append(newEntry)
    
    return newsInfo


def main():
    # you can try out with various rss feeds
    url_espn_rpm = 'https://www.espn.com/espn/rss/rpm/news'
    url_espn_pl = 'http://www.espnfc.com/english-premier-league/23/rss'
    url_cnn = 'http://rss.cnn.com/rss/edition.rss'
    url_reddit = 'http://www.reddit.com/.rss'
    url_bbc = 'http://feeds.bbci.co.uk/news/rss.xml'

    news_info = generalised_parse(url_espn_pl)
    pprint(news_info)


if __name__ == '__main__':
    main()