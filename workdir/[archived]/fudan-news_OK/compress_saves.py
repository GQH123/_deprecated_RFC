import os
import json
import pickle
import shutil
from tqdm import tqdm
import traceback


savepath = './saves/'
compressed_savepath = './csaves'
textpath = os.path.join(compressed_savepath, 'json')
pklpath = os.path.join(compressed_savepath, 'pkl')
binpath = os.path.join(compressed_savepath, 'bin')


def test_textfile(filepath):
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    return is_binary_string(open(filepath, 'rb').read(1024))


def is_textfile(filepath):
    fileext = os.path.splitext(filepath)[1]
    if fileext in ['.json', '.txt', '.py', '.html', '.css', '.js', '.md']:
        return True
    return test_textfile(filepath)


def compress_saves(savestep=10000):
    if not os.path.exists(compressed_savepath):
        os.makedirs(compressed_savepath)
    if not os.path.exists(textpath):
        os.makedirs(textpath)
    if not os.path.exists(pklpath):
        os.makedirs(pklpath)
    if not os.path.exists(binpath):
        os.makedirs(binpath)

    path_text_mapping = {}
    path_pkl_mapping = {}
    path_bin_mapping = {}
    
    path_text_mapping_step = 0
    path_pkl_mapping_step = 0
    path_bin_mapping_step = 0
    
    for root, dirs, files in tqdm(os.walk(savepath)):
        for file in files:
            filepath = os.path.join(root, file) 
            try:
                if file.endswith('.pkl'):
                    data = pickle.load(open(filepath, 'rb'))
                    path_pkl_mapping[filepath] = data
                    if len(path_pkl_mapping) == savestep:
                        path_pkl_mapping_step += 1
                        pickle.dump(path_pkl_mapping, open(os.path.join(pklpath, f'path_pkl_mapping_{path_pkl_mapping_step}.pkl'), 'wb'))
                        path_pkl_mapping = {}
                    continue
                if is_textfile(filepath):
                    # is text
                    try:
                        with open(filepath, 'r') as f:
                            text = f.read()
                    except Exception as e:
                        print(f'warning: {filepath} failed to read as text, will treat as binary, {e}')
                    else:
                        path_text_mapping[filepath] = text
                        if len(path_text_mapping) == savestep:
                            path_text_mapping_step += 1
                            json.dump(path_text_mapping, open(os.path.join(textpath, f'path_text_mapping_{path_text_mapping_step}.json'), 'w'), indent=4, ensure_ascii=False)
                            path_text_mapping = {}
                        continue
                if True:
                    # is binary
                    fileext = os.path.splitext(filepath)[1][1:]
                    extpath = os.path.join(binpath, fileext)
                    if not os.path.exists(extpath):
                        os.makedirs(extpath)
                    filebinpath = os.path.join(extpath, file)
                    if os.path.exists(filebinpath):
                        print(f'warning: {filebinpath} already exists, {filepath} skipped.')
                        continue
                    shutil.copy2(filepath, filebinpath)
                    path_bin_mapping[filepath] = filebinpath
                    if len(path_bin_mapping) == savestep:
                        path_bin_mapping_step += 1
                        json.dump(path_bin_mapping, open(os.path.join(binpath, f'path_bin_mapping_{path_bin_mapping_step}.json'), 'w'), indent=4, ensure_ascii=False)
                        path_bin_mapping = {}
            except Exception as e:
                error_report = f'[{type(e).__name__}] {str(e)}\n{traceback.format_exc()}'
                print(f'failed: {error_report}')
    # final save
    if path_pkl_mapping:
        path_pkl_mapping_step += 1
        pickle.dump(path_pkl_mapping, open(os.path.join(pklpath, f'path_pkl_mapping_{path_pkl_mapping_step}.pkl'), 'wb'))
        path_pkl_mapping = {}
    if path_text_mapping:
        path_text_mapping_step += 1
        json.dump(path_text_mapping, open(os.path.join(textpath, f'path_text_mapping_{path_text_mapping_step}.json'), 'w'), indent=4, ensure_ascii=False)
        path_text_mapping = {}
    if path_bin_mapping:
        path_bin_mapping_step += 1
        json.dump(path_bin_mapping, open(os.path.join(binpath, f'path_bin_mapping_{path_bin_mapping_step}.json'), 'w'), indent=4, ensure_ascii=False)
        path_bin_mapping = {}


compress_saves(1000)