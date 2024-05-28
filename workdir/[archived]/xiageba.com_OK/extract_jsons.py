import os
import json
from tqdm import tqdm
import random
from urllib.parse import urlsplit, urlunsplit
import multiprocessing as mp


savepath = './saves/'
submit_path = './submits/'


def add_error_record(etype, item, checker):
    if etype not in checker:
        checker[etype] = set()
    checker[etype].add(item)


def check_item_info(info):
    checker = {}
    link_type = {}
    link_key = {}
    item = info['id']
    
    if len(info['metadata']) != 3:
        print(f'warning: {item} has {len(info["metadata"])} metadata items, expected 3')
        add_error_record('E1', item, checker)
    for meta in info['metadata']:
        if len(meta) > 1:
            print(f'warning: {item} has metadata item with more than 1 element')
            add_error_record('E2', item, checker)
        if len(meta) == 0:
            print(f'warning: {item} has metadata item with 0 element')
            add_error_record('E3', item, checker)
    info['metadata'] = [meta[0] for meta in info['metadata'] if meta]
    if info['metadata']:
        info['metadata'] = info['metadata'][:3]
        if not info['metadata'][2].startswith('更新：'):
            print(f'warning: {item} has update time item with unexpected format')
            add_error_record('E7', item, checker)
        else:
            info['metadata'][2] = info['metadata'][2][len('更新：'):]
        info['metadata'] = {
            '歌曲名': info['metadata'][0],
            '歌手': info['metadata'][1],
            '更新时间': info['metadata'][2]
        }
    
    for tag in info['tags']:
        if len(tag) > 1:
            print(f'warning: {item} has tag item with more than 1 element')
            add_error_record('E4', item, checker)
        if len(tag) == 0:
            print(f'warning: {item} has tag item with 0 element')
            add_error_record('E5', item, checker)
    info['tags'] = [tag[0] for tag in info['tags'] if tag]
    
    if len(info['lyrics']) > 1:
        print(f'warning: {item} has {len(info["lyrics"])} lyrics item with more than 1 element')
        add_error_record('E6', item, checker)
    info['lyrics'] = info['lyrics'][0] if info['lyrics'] else info['lyrics']
    
    for link in info['links']:
        for k, v in link.items():
            if k not in link_key:
                link_key[k] = 0
            link_key[k] += 1
            if 'http' in v and '://' in v:
                url = urlsplit(v)
                url = f'{url.scheme}://{url.netloc}'
                if url not in link_type:
                    link_type[url] = 0
                link_type[url] += 1
                
    return info, checker, link_type, link_key


def extract_saves_single_process(item):
    if not os.path.exists(os.path.join(savepath, item, f'{item}_info.json')):
        print(f'warning: {item} has no info file')
        info = {
            "metadata": [],
            "tags": [],
            "links": [],
            "lyrics": []
        }
    else:
        info = json.load(open(os.path.join(savepath, item, f'{item}_info.json')))
        if not any(list(info.values())):
            print(f'warning: {item} has empty info file')
    return check_item_info({**{'id': int(item)}, **info})
    

def extract_saves(n_workers=64):
    checker = {}
    link_type = {}
    link_key = {}
    
    all_info = []
    with mp.Pool(n_workers) as pool:
        for info, _checker, _link_type, _link_key in tqdm(pool.imap_unordered(extract_saves_single_process, os.listdir(savepath)), total=len(os.listdir(savepath))):
            all_info.append(info)
            for etype in _checker:
                if etype not in checker:
                    checker[etype] = set()
                checker[etype] |= _checker[etype]
            for k in _link_key:
                if k not in link_key:
                    link_key[k] = 0
                link_key[k] += _link_key[k]
            for k in _link_type:
                if k not in link_type:
                    link_type[k] = 0
                link_type[k] += _link_type[k]
    all_info = sorted(all_info, key=lambda x: x['id'])
    link_type = {k: v for k, v in sorted([(k, v) for k, v in link_type.items()], key=lambda x: -x[1])}
    link_key = {k: v for k, v in sorted([(k, v) for k, v in link_key.items()], key=lambda x: -x[1])}
    json.dump(all_info, open(os.path.join(submit_path, 'all_info.json'), 'w'), indent=4, ensure_ascii=False)
    json.dump(link_type, open(os.path.join(submit_path, 'link_type.json'), 'w'), indent=4, ensure_ascii=False)
    json.dump(link_key, open(os.path.join(submit_path, 'link_key.json'), 'w'), indent=4, ensure_ascii=False)
    for etype in checker:
        checker[etype] = list(checker[etype])
    json.dump(checker, open(os.path.join(submit_path, 'check_result.json'), 'w'), indent=4, ensure_ascii=False)


extract_saves()