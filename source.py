import http.client, urllib.parse
import json

conn = http.client.HTTPConnection('api.mediastack.com')

params = urllib.parse.urlencode({
    'access_key': 'api_key',
    'keywords': 'Zee',
    'limit': 100,
    })

api_request = True
sources_json_object = {}
add_to_existing_file = True

if add_to_existing_file:
    with open('mediastack_sources.json', 'r') as json_file:
        current_source_list = json.load(json_file)['data']

if api_request:
    conn.request('GET', '/v1/sources?{}'.format(params))
    res = conn.getresponse()
    result_json_object = json.loads(res.read().decode('utf-8'))
    if add_to_existing_file:
        result_json_object['data'] = list({x['code']: x for x in result_json_object['data'] + current_source_list}.values())
else:
    with open('mediastack_sources.json', 'r') as json_file:
        result_json_object = json.load(json_file)

print(result_json_object)

with open('mediastack_sources.json', 'w') as json_file:
    json.dump(result_json_object, json_file)