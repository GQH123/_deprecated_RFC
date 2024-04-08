import os
import json
import shutil
from tqdm import tqdm


def remove_subs():
    for vol in tqdm(os.listdir('saves')):
        if os.path.exists(os.path.join('saves', vol, 'subs')):
            print(f'removing {os.path.join("saves", vol, "subs")}')
            shutil.rmtree(os.path.join('saves', vol, 'subs'))


def remove_invalid_posts_and_count():
    count = {}
    total_count = 0
    for vol in tqdm(os.listdir('saves')):
        count[vol] = 0
        if os.path.exists(os.path.join('saves', vol, f'{vol}.html')):
            if_delete = False
            msg = 'unknown'
            with open(os.path.join('saves', vol, f'{vol}.html'), 'r') as f:
                html = f.read()
                if not html:
                    if_delete = True
                    msg = 'empty content'
                if '主题不存在' in html:
                    if_delete = True
                    msg = 'topic not exist'
            if if_delete:
                # shutil.rmtree(os.path.join('saves', vol))
                print(f'{vol} deleted due to {msg}')
            else:
                count[vol] += 1
                total_count += 1
    vol_count_pair = list(count.items())
    vol_count_pair.sort(key=lambda x: int(x[1]), reverse=True)
    count = dict(vol_count_pair)
    print(f'total posts: {total_count}\n{json.dumps(count, indent=4, ensure_ascii=False, sort_keys=False)}')


# remove_subs()
# remove_invalid_posts_and_count()