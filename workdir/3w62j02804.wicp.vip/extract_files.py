import os
import json
from tqdm import tqdm


save_path = 'saves/'
submit_path = 'submits/'
      
            
def remove_invalid():
    for root, dirs, files in tqdm(os.walk(save_path)):
        if '_result.pkl' in files:
            if not os.path.exists(os.path.join(root, 'dir_info.json')):
                print(f'warning: no dir_info.json in {root}')
                continue
            else:
                info = json.load(open(os.path.join(root, 'dir_info.json'), 'r'))
                assert info
        else:
            assert root == save_path or root.endswith('subs')
    
    
def extract_files():
    all_files = []
    for root, dirs, files in tqdm(os.walk(save_path)):
        if '_result.pkl' in files:
            if not os.path.exists(os.path.join(root, 'dir_info.json')):
                print(f'warning: no dir_info.json in {root}')
                continue
            else:
                info = json.load(open(os.path.join(root, 'dir_info.json'), 'r'))
                for item in info['items']:
                    if not item['isDir']:
                        all_files.append(item)
        else:
            assert root == save_path or root.endswith('subs')
    json.dump(all_files, open(os.path.join(submit_path, 'all_files.json'), 'w'), indent=4, ensure_ascii=False)
    
    
def extract_file_stats():
    all_files = json.load(open(os.path.join(submit_path, 'all_files.json'), 'r'))
    print(len(all_files))  # 233217
    stats = {
        'key': set(),
        'extension': {},
        'isDir': set(),
        'isSymlink': set(),
        'mode': set(),
        'resolution': set(),
        'type': set(),
    }
    sizes = []
    for item in tqdm(all_files):
        for key in stats:
            if key == 'key':
                stats['key'].update(item.keys())
            elif key == 'resolution':
                if 'resolution' in item:
                    resolution_dict = item['resolution']
                    if not (len(resolution_dict) == 2 and 'width' in resolution_dict and 'height' in resolution_dict):
                        print(f'warning: invalid resolution {resolution_dict}')
                    else:
                        stats['resolution'].add(f'{resolution_dict["width"]}x{resolution_dict["height"]}')
            elif key == 'extension':
                if 'extension' in item:
                    extension = item['extension'].lower()
                    stats['extension'][extension] = stats['extension'].get(extension, 0) + 1
                else:
                    print(f'warning: no extension in {item}')
            else:
                if key in item:
                    stats[key].add(item[key])
        if 'size' in item:
            sizes.append(item['size'])
            
    extension = stats['extension']
    stats = {key: sorted(list(value)) for key, value in stats.items()}
    stats['extension'] = {key: value for key, value in sorted(extension.items(), key=lambda x: x[1], reverse=True)}
    sizes = sorted(sizes)
    sum_sizes = sum(sizes)
    sizes = {
        '__total__': len(sizes),
        '__sum__': sum_sizes,
        'sizes': sizes,
    }
    json.dump(stats, open(os.path.join(submit_path, 'all_stats.json'), 'w'), indent=4, ensure_ascii=False)
    json.dump(sizes, open(os.path.join(submit_path, 'all_sizes.json'), 'w'), indent=4, ensure_ascii=False)
    print(f'sum_sizes: {sum_sizes}')


def check_audio_file_name(path_prefix=''):
    all_files = json.load(open(os.path.join(submit_path, 'all_files.json'), 'r'))
    ok_name = 0
    bad_name = 0
    for item in tqdm(all_files):
        if 'type' not in item: 
            print(f'warning: no type in {item}')
            continue
        if 'name' not in item: 
            print(f'warning: no name in {item}')
            continue
        if 'path' not in item:
            print(f'warning: no path in {item}')
            continue
        if not item['path'].startswith(path_prefix):
            continue
        if item['type'] != 'audio':
            continue
        if '-' not in item['name'] or len(item['name'].split('-')) != 2:
            bad_name += 1
        else:
            ok_name += 1
    print(f'ok_name: {ok_name}, bad_name: {bad_name}')


# remove_invalid()
# extract_files()
# extract_file_stats()
# check_audio_file_name()  # ok_name: 81160, bad_name: 90898
# check_audio_file_name('/MP3格式音乐166429首1360GB(双击进分类)/其他分类185551首1350GB(双击进分类)/歌手名字分类查找(157745首1120GB)/歌手字母分类')  # ok_name: 32157, bad_name: 2586
# check_audio_file_name('/MP3格式音乐166429首1360GB(双击进分类)/其他分类185551首1350GB(双击进分类)/歌手名字分类查找(157745首1120GB)/歌手专辑分类')  # ok_name: 1124, bad_name: 81947