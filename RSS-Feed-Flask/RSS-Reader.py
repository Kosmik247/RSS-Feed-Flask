import feedparser

feedURL = 'http://feeds.bbci.co.uk/news/health/rss.xml'


def print_news():
  feed = feedparser.parse(feedURL)
  article = feed['entries'][0]

  for article in feed['entries']:
    print(article.get("title"))
    print(article.get("description"))
    print(article.get("link"))

print_news()