import os
import json
import shutil
from tqdm import tqdm


save_path = 'saves/'
new_save_path = '_saves/'
submit_path = 'submits/'


def remove_empty_dir():
    count = 0
    for sub in tqdm(os.listdir(save_path)):
        if os.path.exists(os.path.join(save_path, sub, f'{sub}_info.json')):
            os.rename(os.path.join(save_path, sub), os.path.join(new_save_path, sub))
            continue
        # print(f'remove empty dir: {sub}')
        count += 1
        # os.remove(os.path.join(save_path, sub, f'_item.pkl'))
        # os.rmdir(os.path.join(save_path, sub))
    print(f'remove {count} empty dirs')
    
    
def extract_info():
    all_info = []
    for sub in tqdm(os.listdir(save_path)):
        if os.path.exists(os.path.join(save_path, sub, f'{sub}_info.json')):
            all_info.append(json.load(open(os.path.join(save_path, sub, f'{sub}_info.json'))))
        # print(f'extract info: {sub}')
    json.dump(all_info, open(os.path.join(submit_path, 'all_info.json'), 'w'), indent=4, ensure_ascii=False)


# remove_empty_dir()
# extract_info()