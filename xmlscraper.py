from bs4 import BeautifulSoup
import requests

url = requests.get('http://feeds.bbci.co.uk/news/england/london/rss.xml')
print(url)

soup = BeautifulSoup(url.content, 'xml')
entries = soup.find_all('item')

for entry in entries:
  title = entry.title.text
  summary = entry.description.text
  link = entry.link
  print(f"Title: {title}\n\nSummary: {summary}\n\nLink: {link}\n\n------------------------\n\n")
