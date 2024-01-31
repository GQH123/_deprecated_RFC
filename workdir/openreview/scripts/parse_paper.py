import os
import json
from copy import deepcopy

SAVE_DIR = '../saves/'
CONFERENCE = 'iclr_2024'


def gather_keyword():
    keyword = {}
    keyword[CONFERENCE] = set()
    for root, dirs, files in os.walk(os.path.join(SAVE_DIR, CONFERENCE)):
        for file in files:
            if file.endswith('.json'):
                data = json.load(open(os.path.join(root, file), 'r'))
                for paper in data['notes']:
                    try:
                        for _keyword in paper['content']['keywords']['value']:
                            keyword[CONFERENCE].add(_keyword)
                    except KeyError:
                        continue
    for conf in keyword:
        keyword[conf] = sorted(list(keyword[conf]))
    json.dump(keyword, open('keywords.json', 'w'), indent=4, ensure_ascii=False)
    return keyword
    
    
def gather_focused_keyword():
    keyword = {}
    keyword[CONFERENCE] = set()
    allowed_chars = list(range(ord('a'), ord('z')+1)) + list(range(ord('0'), ord('9')+1)) + [ord('-'), ord('_')]
    for root, dirs, files in os.walk(os.path.join(SAVE_DIR, CONFERENCE)):
        for file in files:
            if file.endswith('.json'):
                data = json.load(open(os.path.join(root, file), 'r'))
                for paper in data['notes']:
                    try:
                        for _keyword in paper['content']['keywords']['value']:
                            _focused_keywords = _keyword.lower().strip().split()
                            for _focused_keyword in _focused_keywords:
                                if all(ord(c) in allowed_chars for c in _focused_keyword):
                                    keyword[CONFERENCE].add(_focused_keyword)
                    except KeyError:
                        continue
    for conf in keyword:
        keyword[conf] = sorted(list(keyword[conf]))
    json.dump(keyword, open('focused_keywords.json', 'w'), indent=4, ensure_ascii=False)
    return keyword


def retrieve_keyword(focused_keywords):
    keywords = json.load(open('./keywords.json', 'r'))
    keywords = keywords[CONFERENCE]
    retrieved_keywords = {}
    for focused_keyword in focused_keywords:
        retrieved_keywords[focused_keyword] = set([])
    for keyword in keywords:
        keyword_part = keyword.strip().split()
        for part in keyword_part:
            for focused_keyword in focused_keywords:
                if part.lower() == focused_keyword:
                    retrieved_keywords[focused_keyword].add(keyword)

    for focused_keyword in focused_keywords:
        retrieved_keywords[focused_keyword] = list(retrieved_keywords[focused_keyword])
    json.dump(retrieved_keywords, open('retrieved_keywords.json', 'w'), indent=4, ensure_ascii=False)
    
    
def match_keyword_and_paper():
    def _attach_percentage(count):
        sum = 0
        for type in count:
            count[type] = len(count[type])
            sum += count[type]
        count['total'] = sum
        for type in count:
            count[type] = f"{count[type]},  {count[type]/count['total']*100:.2f}%"
    retrieved_keywords = json.load(open('./retrieved_keywords.json', 'r'))
    count_template_dict = {
        "oral": set(),
        "spotlight": set(),
        "poster": set(),
        "submitted": set(),
        "total": set(),
    }
    matched_papers = {}
    matched_papers['_count_all'] = deepcopy(count_template_dict)
    matched_papers['_count'] = deepcopy(count_template_dict)
    for focused_keyword in retrieved_keywords:
        matched_papers[focused_keyword] = {}
        matched_papers[focused_keyword]['_count'] = deepcopy(count_template_dict)
        for retrieved_keyword in retrieved_keywords[focused_keyword]:
            matched_papers[focused_keyword][retrieved_keyword] = {}
            matched_papers[focused_keyword][retrieved_keyword]['_count'] = deepcopy(count_template_dict)
            matched_papers[focused_keyword][retrieved_keyword]['papers'] = []
    for root, dirs, files in os.walk(os.path.join(SAVE_DIR, CONFERENCE)):
        for file in files:
            if file.endswith('.json'):
                data = json.load(open(os.path.join(root, file), 'r'))
                paper_type = file.split('_')[0]
                for paper in data['notes']:
                    matched_papers['_count_all'][paper_type].add(paper['forum'])
                    for _keyword in paper['content']['keywords']['value']:
                        for focused_keyword in retrieved_keywords:
                            for retrieved_keyword in retrieved_keywords[focused_keyword]:
                                if retrieved_keyword == _keyword:
                                    # matched_papers[focused_keyword][retrieved_keyword].append(dict(title=paper['content']['title']['value'], url=f"https://openreview.net/forum?id={paper['forum']}", keywords=paper['content']['keywords']['value'], abstract=paper['content']['abstract']['value']))
                                    matched_papers[focused_keyword][retrieved_keyword]['papers'].append(dict(type=paper_type, title=paper['content']['title']['value'], url=f"https://openreview.net/forum?id={paper['forum']}", keywords=paper['content']['keywords']['value'], abstract=paper['content']['abstract']['value']))
                                    matched_papers[focused_keyword][retrieved_keyword]['_count'][paper_type].add(paper['forum'])
                                    matched_papers[focused_keyword]['_count'][paper_type].add(paper['forum'])
                                    try:
                                        matched_papers['_count'][paper_type].add(paper['forum'])
                                    except KeyError as e:
                                        print(matched_papers['_count'])
                                        print(paper_type)
                                        raise e
    _attach_percentage(matched_papers['_count'])
    _attach_percentage(matched_papers['_count_all'])
    for focused_keyword in retrieved_keywords:
        _attach_percentage(matched_papers[focused_keyword]['_count'])
        for retrieved_keyword in retrieved_keywords[focused_keyword]:
            _attach_percentage(matched_papers[focused_keyword][retrieved_keyword]['_count'])
    json.dump(matched_papers, open('matched_papers.json', 'w'), indent=4, ensure_ascii=False)


def sort_focused_keywords_by_accept_rate(threshold=30, field='accept'):
    types = ['oral', 'spotlight', 'poster']
    matched_papers = json.load(open('./matched_papers_full.json', 'r'))
    counts = []
    for focused_keyword in matched_papers:
        if focused_keyword in ['_count_all', '_count']:
            continue
        count = matched_papers[focused_keyword]['_count']
        total = int(count['total'].split(',')[0])
        if total < threshold:
            continue
        count = {type: f"{float(count[type].split(',  ')[-1][:-1]):.2f}%" for type in count}
        count['accept'] = f"{sum([float(count[type][:-1]) for type in types]):.2f}%"
        count['total'] = total
        counts.append({'keyword': focused_keyword, 'count': count})
    counts = sorted(counts, key=lambda x: float(x['count'][field][:-1]), reverse=True)
    counts = {count['keyword']: count['count'] for count in counts}
    json.dump(counts, open(f'sorted_focused_keywords_by_{field}.json', 'w'), indent=4, ensure_ascii=False)


def sort_keywords_by_accept_rate(threshold=10, field='accept'):
    types = ['oral', 'spotlight', 'poster']
    matched_papers = json.load(open('./matched_papers_full.json', 'r'))
    counts = []
    considered = set()
    for focused_keyword in matched_papers:
        if focused_keyword in ['_count_all', '_count']:
            continue
        for keywords in matched_papers[focused_keyword]:
            if keywords in ['_count_all', '_count'] or keywords in considered:
                continue
            considered.add(keywords)
            count = matched_papers[focused_keyword][keywords]['_count']
            total = int(count['total'].split(',')[0])
            if total < threshold:
                continue
            count = {type: f"{float(count[type].split(',  ')[-1][:-1]):.2f}%" for type in count}
            count['accept'] = f"{sum([float(count[type][:-1]) for type in types]):.2f}%"
            count['total'] = total
            counts.append({'keyword': keywords, 'count': count})
    counts = sorted(counts, key=lambda x: float(x['count'][field][:-1]), reverse=True)
    counts = {count['keyword']: count['count'] for count in counts}
    json.dump(counts, open(f'sorted_keywords_by_{field}.json', 'w'), indent=4, ensure_ascii=False)


if __name__ == '__main__':
    # gather_keyword()
    retrieve_keyword(['lora'])
    # retrieve_keyword(gather_focused_keyword()[CONFERENCE])
    match_keyword_and_paper()
    # for field in ['oral', 'spotlight', 'poster', 'accept']:
    #     sort_focused_keywords_by_accept_rate(field=field)
    # for field in ['oral', 'spotlight', 'poster', 'accept']:
    #     sort_keywords_by_accept_rate(field=field)