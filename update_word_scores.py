import json
import re

with open('mediastack_headlines.json', 'r') as json_file:
    headlines = json.load(json_file)['data']

with open('mediastack_word_scores.json', 'r') as json_file:
    word_scores = json.load(json_file)

regex = re.compile('[^a-zA-Z ]')
    
exit = 0

while exit == 0:
    keywords = input('search keywords: ')
    headlines = [x for x in headlines if keywords in x['title']]
    for headline in headlines:
        print(headline)
        update_score = False
        try:
            new_score = float(input('new score: '))
            update_score = True
        except ValueError:
            print('score not updated')
        if update_score:
            title_alphabetic = regex.sub('', headline['title'])
            words = title_alphabetic.split()
            score = 0.0
            for word in words:
                if word.lower() in {x.lower() for x in word_scores}:
                    score += word_scores[word.lower()]
            # print(score)
            suggested_score = new_score - score
            # print(suggested_score)
            if suggested_score != 0:
                for word in words:
                    if word.lower() in {x.lower() for x in word_scores}:
                        word_scores[word.lower()] += suggested_score/len(words)
                    else:
                        word_scores[word.lower()] = suggested_score/len(words)
                print(word_scores)
    exit = input('input 0 to exit: ')      
    
with open('mediastack_word_scores.json', 'w') as json_file:
    json.dump(word_scores, json_file)