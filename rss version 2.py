from rss_parser import Parser
from requests import get

rss_url = "https://feedforall.com/sample.xml"
xml = get(rss_url)


# Чтобы отключить ограничение, просто не указывайте аргумент или используйте None
parser = Parser(xml=xml.content, limit=2)
feed = parser.parse()


print(feed.language)
print(feed.version)


for item in feed.feed:
    print(item.title)
    print(item.description)
