import os
import json
import pickle
import shutil
from tqdm import tqdm


compressed_savepath = './csaves/'
textpath = os.path.join(compressed_savepath, 'json')
pklpath = os.path.join(compressed_savepath, 'pkl')
binpath = os.path.join(compressed_savepath, 'bin')


def decompress_saves():
    print('decompressing path_text_mapping...')
    for path_text_mapping in tqdm(os.listdir(textpath)):
        if not path_text_mapping.startswith('path_text_mapping_') or not path_text_mapping.endswith('.json'):
            print(f'warning: {path_text_mapping} is not a valid path_text_mapping file, skipped.')
            continue
        path_text_mapping = json.load(open(os.path.join(textpath, path_text_mapping), 'r'))
        for path, text in path_text_mapping.items():
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            with open(path, 'w') as f:
                f.write(text)
                
    print('decompressing path_pkl_mapping...')
    for path_pkl_mapping in tqdm(os.listdir(pklpath)):
        if not path_pkl_mapping.startswith('path_pkl_mapping_') or not path_pkl_mapping.endswith('.pkl'):
            print(f'warning: {path_pkl_mapping} is not a valid path_pkl_mapping file, skipped.')
            continue
        path_pkl_mapping = pickle.load(open(os.path.join(pklpath, path_pkl_mapping), 'rb'))
        for path, data in path_pkl_mapping.items():
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            pickle.dump(data, open(path, 'wb'))
            
    print('decompressing path_bin_mapping...')
    for path_bin_mapping in tqdm(os.listdir(binpath)):
        if os.path.isdir(os.path.join(binpath, path_bin_mapping)):
            continue
        if not path_bin_mapping.startswith('path_bin_mapping_') or not path_bin_mapping.endswith('.json'):
            print(f'warning: {path_bin_mapping} is not a valid path_bin_mapping file, skipped.')
            continue
        path_bin_mapping = json.load(open(os.path.join(binpath, path_bin_mapping), 'r'))
        for path, filebinpath in path_bin_mapping.items():
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))
            shutil.copy2(filebinpath, path)


# def compare_with_original_saves(original_savepath, savepath='./saves/'):
#     for root, dirs, files in os.walk(original_savepath):
#         for file in files:
#             original_filepath = os.path.join(root, file)
#             decompressed_filepath = os.path.join(savepath, os.path.relpath(original_filepath, original_savepath))
#             if not os.path.exists(decompressed_filepath):
#                 print(f'warning: {decompressed_filepath} not found.')
#                 continue


# decompress_saves()