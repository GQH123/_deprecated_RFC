import os
import json
from tqdm import tqdm


def extract_infos():
    save_path = '../saves/json/'
    models = sorted(os.listdir(save_path), key=lambda x: int(x))
    all_infos = {}
    all_tags = {}
    # https://civitai.com/api/download/models/62833
    for model in tqdm(models):
        if not os.path.exists(os.path.join(save_path, model, 'model.json')):
            print(f'warning: no model.json found in {model}')
            continue
        data = json.load(open(os.path.join(save_path, model, 'model.json')))
        if 'data' not in data:
            # print(f'warning: no valid data found in {model}/model.json')  # 404
            continue
        data = data['data']
        try:
            model_id = model
            model_type = data['type']
            if model_type not in all_infos:
                all_infos[model_type] = {}
                all_tags[model_type] = {}
            all_infos[model_type][model_id] = data
            for tag in data['tagsOnModels']:
                tag = tag['tag']['name']
                if tag not in all_tags[model_type]:
                    all_tags[model_type][tag] = []
                all_tags[model_type][tag].append(model_id)
        except Exception as e:
            error_report = f'[{type(e).__name__}] {e}'
            print(f'failed: {error_report} in {model}/model.json')
    json.dump(all_infos, open('all_infos.json', 'w'), indent=4, ensure_ascii=False, sort_keys=False)
    json.dump(all_tags, open('all_tags.json', 'w'), indent=4, ensure_ascii=False, sort_keys=False)
    for type in all_tags:
        for tag in all_tags[type]:
            all_tags[type][tag] = len(all_tags[type][tag])
        all_tags[type] = dict(sorted(all_tags[type].items(), key=lambda x: x[1], reverse=True))
    json.dump(all_tags, open('all_tags_count.json', 'w'), indent=4, ensure_ascii=False, sort_keys=False)


def extract_type_infos(infos):
    for type in infos:
        result = {}
        count = len(infos[type])
        result['infos'] = infos[type]
        result['meta'] = {}
        result['meta']['count'] = count
        json.dump(result, open(f'./{type}_infos.json', 'w'), indent=4, ensure_ascii=False, sort_keys=False)


def extract_type_tags(tags):
    for type in tags:
        result = {}
        count = len(tags[type])
        result['tags'] = tags[type]
        result['meta'] = {}
        result['meta']['count'] = count
        json.dump(result, open(f'./{type}_tags.json', 'w'), indent=4, ensure_ascii=False, sort_keys=False)


def extract_type_tags_count(tags_count):
    for type in tags_count:
        result = {}
        count = len(tags_count[type])
        result['tags_count'] = tags_count[type]
        result['meta'] = {}
        result['meta']['count'] = count
        json.dump(result, open(f'./{type}_tags_count.json', 'w'), indent=4, ensure_ascii=False, sort_keys=False)


if __name__ == '__main__':
    extract_infos()
    infos = json.load(open('./all_infos.json'))
    extract_type_infos(infos)
    tags = json.load(open('./all_tags.json'))
    extract_type_tags(tags)
    tags_count = json.load(open('./all_tags_count.json'))
    extract_type_tags_count(tags_count)