import re
import os
import json


def parse():
    host = 'https://yufukirima.sakura.ne.jp'
    save_path = '../saves/galleries'
    result = {}
    for html in os.listdir(save_path):
        if not html.endswith('.html'):
            continue
        post = html.split('.')[0]
        with open(os.path.join(save_path, html), 'r') as f:
            html = f.read()
        links = re.findall('<img src="([^\"]*)"', html)
        links = [host + link for link in links]
        result[post] = links
    return result


result = parse()
json.dump(result, open('galleries.json', 'w'), indent=4, ensure_ascii=False, sort_keys=True)