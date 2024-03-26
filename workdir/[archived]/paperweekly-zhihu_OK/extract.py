import os
import json


os.makedirs('submit', exist_ok=True)
jsons = os.listdir('saves')
for _json in jsons:
    data = json.load(open(f'saves/{_json}/{_json}.json', 'r'))
    articles = data['data']
    for article in articles:
        id = article['id']
        content = article['content']
        title = article['title']
        result = {
            'id': id,
            'content': content,
            'title': title,
        }
        if os.path.exists(f'submit/{str(id)}.json'):
            print(f'{id} exists')
        with open(f'submit/{str(id)}.json', 'w') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)