import os
import json
import shutil
from tqdm import tqdm


def remove_subs():
    for vol in tqdm(os.listdir('saves')):
        if os.path.exists(os.path.join('saves', vol, 'subs')):
            os.system(f'rm -r "{os.path.join("saves", vol, "subs")}"')
            
            
def remove_cookies_invalid_paper():
    for vol in tqdm(os.listdir('saves')):
        if os.path.exists(os.path.join('saves', vol, 'subs')):
            for paper in os.listdir(os.path.join('saves', vol, 'subs')):
                if os.path.exists(os.path.join('saves', vol, 'subs', paper, f'{paper}.html')):
                    if_delete = False
                    with open(os.path.join('saves', vol, 'subs', paper, f'{paper}.html'), 'r') as f:
                        first_line = f.readline()
                        if 'Cookie失效，请刷新页面' in first_line:
                            if_delete = True
                    if if_delete:
                        shutil.rmtree(os.path.join('saves', vol, 'subs', paper))
                        print(f'{vol}/{paper} deleted due to invalid cookies')
                        

def remove_empty_paper():
    for vol in tqdm(os.listdir('saves')):
        if os.path.exists(os.path.join('saves', vol, 'subs')):
            for paper in os.listdir(os.path.join('saves', vol, 'subs')):
                if_delete = False
                if os.path.exists(os.path.join('saves', vol, 'subs', paper, f'{paper}.html')):
                    with open(os.path.join('saves', vol, 'subs', paper, f'{paper}.html'), 'r') as f:
                        content = f.read()
                        if not content:
                            if_delete = True
                else:
                    if_delete = True
                if if_delete:
                    shutil.rmtree(os.path.join('saves', vol, 'subs', paper))
                    print(f'{vol}/{paper} deleted due to empty content')


def count_paper():
    count = {}
    total_count = 0
    for vol in tqdm(os.listdir('saves')):
        count[vol] = 0
        if os.path.exists(os.path.join('saves', vol, 'subs')):
            for paper in os.listdir(os.path.join('saves', vol, 'subs')):
                if os.path.exists(os.path.join('saves', vol, 'subs', paper, f'{paper}.html')):
                    count[vol] += 1
                    total_count += 1
    vol_count_pair = list(count.items())
    vol_count_pair.sort(key=lambda x: int(x[1]), reverse=True)
    count = dict(vol_count_pair)
    print(f'total papers: {total_count}\n{json.dumps(count, indent=4, ensure_ascii=False, sort_keys=False)}')
                    
                        

# remove_subs()
# remove_cookies_invalid_paper()
# remove_empty_paper()
count_paper()