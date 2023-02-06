from bs4 import BeautifulSoup
import requests
import json

url = 'https://stackoverflow.com/questions/33686747/save-a-list-to-a-txt-file'


def hackernews_rss(url):
    article_list = []
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, features='xml')
        articles = soup.findAll('item')
        for a in articles:
            title = a.find('title').text
            link = a.find('link').text
            published = a.find('pubDate').text
            article = {
                'title': title,
                'link': link,
                'published': published
            }
            article_list.append(article)
            return save_function(article_list)

    except Exception as e:
        print('The scraping job failed. See exception: ')
        print(e, 'Starting scraping')


def save_function(article_list):
    with open('articles.txt', 'w') as outfile:
        json.dump(article_list, outfile)


hackernews_rss(url)
print('Finished scraping')
