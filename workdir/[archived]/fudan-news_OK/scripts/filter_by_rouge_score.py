import os
import json
import shutil
from tqdm import tqdm


def parse_raw_qa():
    """
        fail mode:
            - `if not (line.startswith('问:') or line.startswith('答:')):`  # failed_qa_count: 1907, qa_count: 32970
            - ...
    """
    # from rouge_score import rouge_scorer
    from rouge_chinese import Rouge
    import jieba
    import random
    
    # scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)
    rouge = Rouge()
    remained_count = {}
    datapath = '../submits/fudan_news_qa_full_processed/qa/'
    # failed_qa_count = {}
    failed_files = json.load(open('failed_files.json', 'r'))
    for file in tqdm(os.listdir(datapath)):
        if file in failed_files:
            # raw_file = file.replace('_qa', '')
            os.remove(os.path.join(datapath, file))
            # os.remove(os.path.join(datapath, '..', 'raw', raw_file))
            continue
        parsed_qa = []
        data = json.load(open(os.path.join(datapath, file)))
        for raw_qa in data['qa']:
            raw_qa_lines = [line for line in raw_qa.split('\n') if line]
            state = None
            have_Q = False
            have_A = False
            Q_line = ''
            A_line = ''
            for lid, line in enumerate(raw_qa_lines):
                if line.startswith('问:'):
                    if have_Q:
                        state = 'F_1'
                        break
                    have_Q = True
                    Q_line += line
                    state = 'Q'
                elif line.startswith('答:'):
                    if not have_Q:
                        state = 'F_2'
                        break
                    if state != 'Q':
                        state = 'F_3'
                        break
                    have_A = True
                    A_line += line
                    state = 'A'
                else:
                    if state is None:
                        state = 'F_4'
                        break
                    if state == 'Q':
                        Q_line += line
                    elif state == 'A':
                        A_line += line
            if not state.startswith('F'):
                if state != 'A':
                    state = 'F_5'
                if not Q_line:
                    state = 'F_6'
                if not A_line:
                    state = 'F_7'
            if state.startswith('F'):
                assert False  # after filtering, there should not be any corrupted json files
            else:
                parsed_qa.append((Q_line[2:], A_line[2:]))
        _parsed_qa = []
        # random.shuffle(parsed_qa)
        for q, a in parsed_qa:
            if not _parsed_qa:
                _parsed_qa.append((q, a))
                continue
            if '�' in q or '�' in a:
                continue
            rouge_scores = [rouge.get_scores(' '.join(jieba.cut(q)), ' '.join(jieba.cut(compared_q)))[0]['rouge-l']['p'] for compared_q, _ in _parsed_qa]
            # print(len(rouge_scores))
            # print(rouge_scores)
            # print(json.dumps(rouge_scores, indent=4))
            if max(rouge_scores) > 0.5:
                continue
            _parsed_qa.append((q, a))
        parsed_qa = _parsed_qa
        data['parsed_qa'] = parsed_qa
        data['parsed_qa_count'] = len(parsed_qa)
        remained_count[len(parsed_qa)] = remained_count.get(len(parsed_qa), 0) + 1
        print(f'{file}: {len(parsed_qa)}')
        json.dump(data, open(os.path.join(datapath, file), 'w'), indent=4, ensure_ascii=False)
    print(json.dumps(remained_count, indent=4))
    json.dump(remained_count, open('remained_count.json', 'w'), indent=4, ensure_ascii=4)


def count_category_average():
    datapath = '../submits/fudan_news_qa_full_processed/qa/'
    failed_files = json.load(open('failed_files.json', 'r'))
    category_count = {}
    for file in tqdm(os.listdir(datapath)):
        if file in failed_files:
            os.remove(os.path.join(datapath, file))
            continue
        data = json.load(open(os.path.join(datapath, file)))
        category = data['category']
        filtered_qa_count = data['parsed_qa_count']
        category_count[category] = category_count.get(category, [])
        category_count[category].append(filtered_qa_count)
    category_average = {}
    for category, counts in category_count.items():
        category_average[category] = sum(counts) / len(counts)
    # sort by average
    category_average = {k: {'average': v} for k, v in sorted(category_average.items(), key=lambda item: item[1], reverse=True)}
    for k in category_average.keys():
        category_average[k]['count'] = len(category_count[k])
        category_average[k]['total'] = sum(category_count[k])
    print(json.dumps(category_average, indent=4, ensure_ascii=False))
    json.dump(category_average, open('category_average.json', 'w'), indent=4, ensure_ascii=False)
    
    
def filter_qa():
    datapath = '../submits/fudan_news_qa_full_processed/qa/'
    filtered_path = '../submits/fudan_news_qa_full_processed/qa_filtered/'
    if os.path.exists(filtered_path):
        shutil.rmtree(filtered_path)
    os.makedirs(filtered_path)
    failed_files = json.load(open('failed_files.json', 'r'))
    filtered_category = [
        '党建动态',
    ]
    n_qa_threshold = 6
    year_threshold = 2023
    for file in tqdm(os.listdir(datapath)):
        if file in failed_files:
            os.remove(os.path.join(datapath, file))
            continue
        data = json.load(open(os.path.join(datapath, file)))
        if data['category'] in filtered_category or data['parsed_qa_count'] < n_qa_threshold:
            continue
        if '发布时间' not in data['metas']:
            continue
        date = data['metas']['发布时间'].split('-')
        if len(date) != 3:
            continue
        year = int(date[0])
        if year not in range(year_threshold, 2024+1):
            continue
        # copy to filtered path
        shutil.copy2(os.path.join(datapath, file), os.path.join(filtered_path, file))
        
        
def merge_qa():
    import random

    datapath = '../submits/fudan_news_qa_full_processed/qa_filtered/'
    savepath = '../submits/fudan_news_qa_full_processed'
    failed_files = json.load(open('failed_files.json', 'r'))
    all_qas = []
    for file in tqdm(os.listdir(datapath)):
        if file in failed_files:
            os.remove(os.path.join(datapath, file))
            continue
        data = json.load(open(os.path.join(datapath, file)))
        all_qas += data['parsed_qa']
    random.shuffle(all_qas)
    json.dump(all_qas, open(os.path.join(savepath, 'fudan_news_qa.json'), 'w'), indent=4, ensure_ascii=False)
    print(len(all_qas))


# parse_raw_qa()
# count_category_average()
# filter_qa()
merge_qa()