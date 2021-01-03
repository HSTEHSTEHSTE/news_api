import json
from fuzzywuzzy import fuzz
import datetime

from newsapi import NewsApiClient
api = NewsApiClient(api_key='api-key')

api_call = False

json_headlines = None
articles_headlines = None

yesterday_datetime = (datetime.datetime.today() - datetime.timedelta(days = 1)).strftime('%Y-%m-%d')

if api_call:
    # Retrieve full top headline json object
    # {'status', 'totalResults', 'articles': [articles]}
    # article: {{'source': {'id', 'name'}}, 'author', 'title', 'description', 'url', 'urlToImage', 'publishedAt', 'content'}
    json_headlines = api.get_everything(q = 'stock', from_param = yesterday_datetime, language = 'en')
    # json_headlines = api.get_top_headlines()
    articles_headlines = json_headlines['articles']

    with open('headlines.json', 'w') as json_file:
        json.dump(json_headlines, json_file)
else:
    with open('headlines.json', 'r') as json_file:
        json_headlines = json.load(json_file)
    articles_headlines = json_headlines['articles']

headlines = []
source_blacklist = ["Entrepreneur", "Android Central"]
for article in articles_headlines:
    duplicate = False
    blacklisted = False
    for headline in headlines:
        if fuzz.ratio(headline, article['title']) > 80:
            duplicate = True
    if article['source']['name'] in source_blacklist:
        blacklisted = True
    if not duplicate and not blacklisted:
        headlines.append(article['title'])
        print(article['title'], ": ", article['source']['name'])
    # print(article['source']['name'])
