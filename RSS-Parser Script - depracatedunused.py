# Import library used for parsing module
import feedparser

feedURL = 'https://www.bbc.co.uk/news/uk-66940513?at_medium=RSS&at_campaign=KARANGA'

# Testing function to obtain elements of parser I require.
def print_news():
  feed = feedparser.parse(feedURL)
  article = feed['entries'][0]
  print(feed.get('article'))
  for article in feed['entries']:
    print(article.get("title"))
    print(article.get("description"))
    print(article.get("link"))

print_news()


# This file is an initial testing example of how the feedparser library is used within the program.