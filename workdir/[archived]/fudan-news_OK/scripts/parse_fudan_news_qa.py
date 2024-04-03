import os
import json
import shutil
from tqdm import tqdm


def extract_qa_and_raw():
    datapath = '../filtered_news_qa'
    savepath = '../filtered_news'
    
    for file in tqdm(os.listdir(datapath)):
        if file.endswith('.json'):
            try:
                if '_qa.json' in file:
                    shutil.copyfile(os.path.join(datapath, file), os.path.join(savepath, 'qa', file))
                else:
                    shutil.copyfile(os.path.join(datapath, file), os.path.join(savepath, 'raw', file))
            except BlockingIOError:
                print(f'failed to copy {file}')
                continue
        else:
            print(f'warning, {file} is not a json file')
            
            
def parse_raw_qa():
    """
        fail mode:
            - `if not (line.startswith('问:') or line.startswith('答:')):`  # failed_qa_count: 1907, qa_count: 32970
            - ...
    """
    datapath = '../filtered_news/qa'
    failed_qa_count = {}
    qa_count = 0
    failed_files = json.load(open('failed_files.json', 'r'))
    parsed_qa = []
    for file in tqdm(os.listdir(datapath)):
        if file in failed_files:
            raw_file = file.replace('_qa', '')
            os.remove(os.path.join(datapath, file))
            os.remove(os.path.join(datapath, '..', 'raw', raw_file))
            continue
        data = json.load(open(os.path.join(datapath, file)))
        for raw_qa in data['qa']:
            qa_count += 1
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
    json.dump(parsed_qa, open(os.path.join(datapath, '..', 'parsed_qa.json'), 'w'), indent=4, ensure_ascii=False)
    print(len(parsed_qa))
    # failed_files = list(set(failed_files))
    # print(f'failed_qa_count:\n{json.dumps(failed_qa_count, indent=4, ensure_ascii=False)}')
    # print(f'failed_files:\n{json.dumps(failed_files, indent=4, ensure_ascii=False)}')
    # print(f'qa_count: {qa_count}')


def extract_raw_to_one_file():
    datapath = '../filtered_news/raw'
    data = []
    for file in tqdm(os.listdir(datapath)):
        data.append(json.load(open(os.path.join(datapath, file))))
    json.dump(data, open(os.path.join(datapath, '..', 'raw.json'), 'w'), indent=4, ensure_ascii=False)
    print(len(data))


# extract_qa_and_raw()
parse_raw_qa()
# extract_raw_to_one_file()