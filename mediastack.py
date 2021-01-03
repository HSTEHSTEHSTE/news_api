import http.client, urllib.parse
import json
import datetime
from fuzzywuzzy import fuzz
import re
import random
import numpy as np

conn = http.client.HTTPConnection('api.mediastack.com')

countries = ['au', 'br', 'ca', 'cn', 'fr', 'de', 'hk', 'in', 'it', 'jp', 'nl', 'nz', 'sa', 'sg', 'kr', 'tw', 'tr', 'ae', 'ua', 'gb', 'us']

source_exclude_list = ['Zee Business', 'Focus']

yesterday_datetime = (datetime.datetime.today() - datetime.timedelta(days = 1)).strftime('%Y-%m-%d')
today_datatime = datetime.datetime.today().strftime('%Y-%m-%d')
datetime = yesterday_datetime + ', ' + today_datatime

headline_number = 10

randomised_results = False
prompt_for_score_update = False

word_scores = {
    'nba': -10,
    'chinese': 5,
    'india': -1,
    'climate': -1,
    'electoral': -2,
    'indian': -1,
    'bullish': 1,
    'recovery': 1,
    'tariffs': 1,
    'tariff': 1,
    'consolidation': 1,
    'investors': 1,
    'merger': 3,
    'growth': 1,
}

with open('mediastack_word_scores.json', 'r') as json_file:
    word_scores = json.load(json_file)

regex = re.compile('[^a-zA-Z ]')

params = urllib.parse.urlencode({
    'access_key': 'api_key',
    'categories': 'business',
    'sort': 'published_desc',
    'limit': 100,
    'languages': 'en,zh,-de,-nl',
    'countries': 'cn,fr,de,hk,jp,sg,tw,gb,us,-in',
    'data': datetime,
    'sources': '-zeebiz,-focus',
    })

api_request = False
result_json_object = {}

if api_request:
    conn.request('GET', '/v1/news?{}'.format(params))
    res = conn.getresponse()
    result_json_object = json.loads(res.read().decode('utf-8'))
else:
    with open('mediastack_headlines.json', 'r') as json_file:
        result_json_object = json.load(json_file)

# print(result_json_object)

headlines_list = result_json_object['data']
headlines_selected = []
score_list = []
for data_item in headlines_list:
    duplicate = False
    for headline in headlines_selected:
        if fuzz.ratio(data_item['title'], headline['title']) > 80:
            duplicate = True
    if data_item['source'] not in source_exclude_list and not duplicate:
        title_alphabetic = regex.sub('', data_item['title'])
        words = title_alphabetic.split()
        # print(words)
        score = 0
        for word in words:
            if word.lower() in {x.lower() for x in word_scores}:
                score += word_scores[word.lower()]
        data_item['score'] = score
        score_list.append(max(3 + score, 0))
        headlines_selected.append(data_item)

# print(headlines_selected)

weights = [x/sum(score_list) for x in score_list]
headlines_curated = np.random.choice(headlines_selected, headline_number, True, weights)

headlines_selected = sorted(headlines_selected, key = lambda x: x['score'], reverse = True)
headlines_selected = headlines_selected[:headline_number]

if not randomised_results:
    headlines_curated = headlines_selected

for data_item in headlines_curated:
    print(data_item['title'], ' - ', data_item['source']) #, ' at ', data_item['published_at'], ' with score: ', data_item['score'])
    if prompt_for_score_update:
        suggested_score = 0
        try:
            suggested_score = float(input('Input suggested score: '))
        except ValueError:
            print('invalid score')
        suggested_score = suggested_score - data_item['score']
        if suggested_score != 0:
            title_alphabetic = regex.sub('', data_item['title'])
            words = title_alphabetic.split()
            for word in words:
                if word.lower() in {x.lower() for x in word_scores}:
                    word_scores[word.lower()] += suggested_score/len(words)
                else:
                    word_scores[word.lower()] = suggested_score/len(words)

print(result_json_object['pagination']['total'])

if prompt_for_score_update:
    print(word_scores)

with open('mediastack_headlines.json', 'w') as json_file:
    json.dump(result_json_object, json_file)
    
with open('mediastack_word_scores.json', 'w') as json_file:
    json.dump(word_scores, json_file)