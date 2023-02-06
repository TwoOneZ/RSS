from rss_parser import Parser
from requests import get

rss_url = "https://feedforall.com/sample.xml"
xml = get(rss_url)

# Чтобы отключить ограничение, просто не указывайте аргумент или используйте None
parser = Parser(xml=xml.content, limit=None)
feed = parser.parse()

# Распечатать метаданные фида
print(feed.language)
print(feed.version)

# Итеративно печатать элементы фида
for item in feed.feed:
    print(item.title)
    print(item.description)