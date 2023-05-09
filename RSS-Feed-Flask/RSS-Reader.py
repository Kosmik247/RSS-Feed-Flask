from bs4 import BeautifulSoup
import requests
from website import db 





def get_rss(url):
  url = requests.get('https://feeds.bbci.co.uk/news/england/london/rss.xml')
  soup = BeautifulSoup(url.content, 'xml')
  entries = soup.find_all('item')

  for entry in entries:
    title = entry.title.text
    summary = entry.description.text
    link = entry.link
    print(f"Title: {title}\n\nSummary: {summary}\n\nLink: {link}\n\n------------------------\n\n")

get_rss()