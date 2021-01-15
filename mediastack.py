import http.client, urllib.parse
import json
import datetime
from fuzzywuzzy import fuzz
import re
import random
import numpy as np
import time

api_key = ''

conn = http.client.HTTPConnection('api.mediastack.com')

countries = ['au', 'br', 'ca', 'cn', 'fr', 'de', 'hk', 'in', 'it', 'jp', 'nl', 'nz', 'sa', 'sg', 'kr', 'tw', 'tr', 'ae', 'ua', 'gb', 'us']

source_exclude_list = ['Zee Business', 'Focus']

yesterday_datetime = (datetime.datetime.today() - datetime.timedelta(days = 1)).strftime('%Y-%m-%d')
today_datatime = datetime.datetime.today().strftime('%Y-%m-%d')
datetime = yesterday_datetime + ', ' + today_datatime

headline_number = 20
page_limit = 100

randomised_results = False
prompt_for_score_update = False
prompt_for_word_category_score_update = True
verbose = False
api_request = False
api_request_page_limit = 5
time_program = True

start_time = 0
current_time = 0
if time_program:
    start_time = time.time()

with open('mediastack_word_scores.json', 'r') as json_file:
    word_scores = json.load(json_file)

word_categories = {
    '0':  {'name': 'no_meaning',    'score': 0},
    '1':  {'name': 'sports',        'score': -1},
    '2':  {'name': 'equities',      'score': 5},
    '3':  {'name': 'blockchain',    'score': 1},
    '4':  {'name': 'China',         'score': 5},
    '5':  {'name': 'US',            'score': 2},
    '6':  {'name': 'politics',      'score': -1},
    '7':  {'name': 'covid',         'score': 0},
    '8':  {'name': 'Asia',          'score': 2},
    '9':  {'name': 'Europe',        'score': 1},
    '10': {'name': 'commodities',   'score': 3},
    '11': {'name': 'tech',          'score': 1},
    '12': {'name': 'economics',     'score': 3},
}
word_category_number = 13

def list_word_categories():
    for word_category in word_categories:
        print(word_category, ': ', word_categories[word_category]['name'], end = '; ')
    print()

word_category_scores = {}
with open('mediastack_word_categories.json', 'r') as json_file:
    word_category_scores = json.load(json_file)

source_scores = {
    'Zee Business': -10,
    'focus': -10,
}
with open('mediastack_source_scores.json', 'r') as json_file:
    source_scores = json.load(json_file)
source_shift_step = 0.10

regex = re.compile('[^a-zA-Z ]')

request_params = {
    'access_key': api_key,
    'categories': 'business',
    'sort': 'published_desc',
    'limit': page_limit,
    'languages': 'en,zh,-de,-nl',
    'countries': 'cn,fr,de,hk,jp,sg,tw,gb,us,-in',
    'data': datetime,
    'sources': '-zeebiz,-focus',
}

result_json_object = {}
if api_request:
    page = 0    
    while page < api_request_page_limit:
        offset = page * page_limit
        request_params['offset'] = offset
        params = urllib.parse.urlencode(request_params)
        conn.request('GET', '/v1/news?{}'.format(params))
        res = conn.getresponse()
        result_json_object_temp = json.loads(res.read().decode('utf-8'))
        if 'data' in result_json_object:
            result_json_object['data'] += result_json_object_temp['data']
        else:
            result_json_object = result_json_object_temp
        page += 1
        if 'error' in result_json_object:
            print(result_json_object)
            page = api_request_page_limit
else:
    with open('mediastack_headlines.json', 'r') as json_file:
        result_json_object = json.load(json_file)

if time_program:
    current_time = time.time()
    print("Files loaded and api requests made: ", current_time - start_time)
    start_time = current_time

# Each category is represented by a dimension

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
if time_program:
    current_time = time.time()
    print("Calculate word scores: ", current_time - start_time)
    start_time = current_time

weights = [x / sum(score_list) for x in score_list]
headlines_curated = np.random.choice(headlines_selected, headline_number, True, weights)

headlines_selected = sorted(headlines_selected, key = lambda x: x['score'], reverse = True)
headlines_selected = headlines_selected[:headline_number]

if not randomised_results:
    headlines_curated = headlines_selected

for data_item in headlines_curated:
    if verbose:
        print(data_item['title'], ' - ', data_item['source'], ' at ', data_item['published_at'], ' with score: ', data_item['score'])
    else:
        print(data_item['title'], ' - ', data_item['source'])
    if prompt_for_score_update:
        suggested_score = 0
        try:
            suggested_score = float(input('Input suggested score (-5, -2, 0, 2, 5): '))
        except ValueError:
            print('invalid score')
        suggested_score = suggested_score - data_item['score']
        if suggested_score != 0:
            title_alphabetic = regex.sub('', data_item['title'])
            words = title_alphabetic.split()
            for word in words:
                if word.lower() in {x.lower() for x in word_scores}:
                    word_scores[word.lower()] += suggested_score / len(words)
                else:
                    word_scores[word.lower()] = suggested_score / len(words)
            source = data_item['source']
            if source in source_scores:
                source_scores[source] += suggested_score * source_shift_step
            else:
                source_scores[source] = suggested_score * source_shift_step
    if prompt_for_word_category_score_update:
        title_alphabetic = regex.sub('', data_item['title'])
        words = title_alphabetic.split()
        word = random.choice(words)
        #print(word_category_scores)
        if True: #not word in word_category_scores:
        #for word in words:
            word = word.lower()
            new_category = -1
            try:
                list_word_categories()
                message = 'Input new category for ' + word + ':'
                new_category = int(input(message))
            except ValueError:
                print('invalid new category')
            if new_category > -1 and new_category < word_category_number:
                if word in word_category_scores:
                    word_category_scores[word][word_categories[str(new_category)]['name']] += 1
                    word_category_scores[word]['count'] += 1
                else:
                    word_category_scores[word] = {'count': 1, word_categories[str(new_category)]['name']: 1}
                    
if time_program:
    current_time = time.time()
    print("Selected headlines: ", current_time - start_time)
    start_time = current_time

if verbose:
    # print(result_json_object)
    print(result_json_object['pagination']['total'])

if prompt_for_score_update:
    # print(word_scores)
    print(source_scores)

with open('mediastack_headlines.json', 'w') as json_file:
    json.dump(result_json_object, json_file)
    
with open('mediastack_word_scores.json', 'w') as json_file:
    json.dump(word_scores, json_file)
    
with open('mediastack_source_scores.json', 'w') as json_file:
    json.dump(source_scores, json_file)
    
with open('mediastack_word_categories.json', 'w') as json_file:
    json.dump(word_category_scores, json_file)