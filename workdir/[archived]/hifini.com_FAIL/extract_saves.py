import os
import json
from tqdm import tqdm
import random


savepath = './saves/'
savedlogpath = './saved_logs/'
# audiopath = './audios/'


def extract_saves():
    fileext_count = {}
    # if not os.path.exists(audiopath):
        # os.makedirs(audiopath)
    for subdir in tqdm(os.listdir(savepath)):
        if not os.path.exists(os.path.join(savepath, subdir, 'subs')):
            continue
        audios = os.listdir(os.path.join(savepath, subdir, 'subs'))
        for audio in audios:
            files = os.listdir(os.path.join(savepath, subdir, 'subs', audio))
            for file in files:
                if file.startswith(audio):
                    fileext = file.split('.')[-1]
                    if fileext not in fileext_count:
                        fileext_count[fileext] = 0
                    fileext_count[fileext] += 1
    json.dump(fileext_count, open(os.path.join(savedlogpath, 'fileext_count.json'), 'w'), indent=4, ensure_ascii=False)


extract_saves()