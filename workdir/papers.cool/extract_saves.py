import os
import json
from tqdm import tqdm
import random


savepath = './saves/'
jsonpath = './jsons/'
jsonpath_only_with_contents = './jsons/with_contents/'
sampled_path = './submits/'


def extract_saves(only_with_contents=False):
    paper_info_dict_full = {}
    _jsonpath = jsonpath
    if only_with_contents:
        _jsonpath = jsonpath_only_with_contents
    if not os.path.exists(_jsonpath):
        os.makedirs(_jsonpath)
    for subdir in tqdm(os.listdir(savepath)):
        if not os.path.exists(os.path.join(savepath, subdir, 'subs')):
            continue
        paper_info = json.load(open(os.path.join(savepath, subdir, f'{subdir}_info.json')))
        paper_info_dict = {}
        paper_id_to_key = {}
        for paper_item in paper_info:
            paper_key = paper_item[0].split('?paper')[-1]
            paper_id = f'{subdir}_{paper_key}'
            paper_id_to_key[paper_id] = paper_key
            paper_type, paper_tag = subdir.split('_')
            paper_info_dict[paper_key] = {
                'meta': {
                    'title': paper_item[2],
                    'type': paper_type,
                    'source': paper_tag,
                    'kimi_link': paper_item[0],
                    'pdf_link': paper_item[1],
                }
            }
        for paper in os.listdir(os.path.join(savepath, subdir, 'subs')):
            assert paper in paper_id_to_key
            if not os.path.exists(os.path.join(savepath, subdir, 'subs', paper, f'{paper}.html')):
                continue
            # ignore html content checking here
            with open(os.path.join(savepath, subdir, 'subs', paper, f'{paper}.html'), 'r') as f:
                paper_info_dict[paper_id_to_key[paper]]['content'] = f.read()
        if only_with_contents:
            for paper_key in list(paper_info_dict.keys()):
                if 'content' not in paper_info_dict[paper_key]:
                    del paper_info_dict[paper_key]
        json.dump(paper_info_dict, open(os.path.join(_jsonpath, f'{subdir}.json'), 'w'), indent=4, ensure_ascii=False)
        paper_info_dict_full = {**paper_info_dict_full, **paper_info_dict}
    json.dump(paper_info_dict_full, open(os.path.join(_jsonpath, 'full.json'), 'w'), indent=4, ensure_ascii=False)


def random_sample_papers_with_contents(n_samples='all', no_arxiv=False, only_arxiv=False):
    if not os.path.exists(sampled_path):
        os.makedirs(sampled_path)
    if no_arxiv:
        full_papers_with_contents = {key: item for key, item in json.load(open(os.path.join(jsonpath_only_with_contents, 'full.json'))).items() if item['meta']['type'] != 'arxiv'}
    elif only_arxiv:
        full_papers_with_contents = {key: item for key, item in json.load(open(os.path.join(jsonpath_only_with_contents, 'full.json'))).items() if item['meta']['type'] == 'arxiv'}
    else:
        full_papers_with_contents = json.load(open(os.path.join(jsonpath_only_with_contents, 'full.json')))
    all_paper_keys = list(full_papers_with_contents.keys())
    if n_samples == 'all':
        n_samples = len(all_paper_keys)
    assert len(all_paper_keys) >= n_samples
    sampled_papers = []
    for i in tqdm(range(n_samples)):
        random_paper_key = random.choice(all_paper_keys)
        all_paper_keys.remove(random_paper_key)
        sampled_papers.append(full_papers_with_contents[random_paper_key])
    json.dump(sampled_papers, open(os.path.join(sampled_path, f'sampled_papers_{n_samples}.json'), 'w'), indent=4, ensure_ascii=False)


# extract_saves(True)
# extract_saves(False)
random_sample_papers_with_contents(only_arxiv=True)