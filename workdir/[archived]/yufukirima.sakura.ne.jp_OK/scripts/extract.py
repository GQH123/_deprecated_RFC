import os
import re
import json


posts = os.listdir('saves/posts')

result = {}
for post in posts:
    if not os.path.exists(f'saves/posts/{post}/{post}.json') and not os.path.exists(f'saves/posts/{post}/{post}.txt'):
        continue
    if os.path.exists(f'saves/posts/{post}/{post}.txt'):
        data = json.load(open(f'saves/posts/{post}/{post}.txt'))
    else:
        data = json.load(open(f'saves/posts/{post}/{post}.json'))
    try:
        text = data['body']['body']['text']
    except Exception:
        continue
    links = re.findall('【(https://yufukirima.sakura.ne.jp/events/show.php[^】]*)', text)
    # assert len(links) <= 1
    if links:
        result[f'https://yufukirima.fanbox.cc/posts/{post}'] = links
        
json.dump(result, open('links.json', 'w'), ensure_ascii=False, indent=4, sort_keys=True)