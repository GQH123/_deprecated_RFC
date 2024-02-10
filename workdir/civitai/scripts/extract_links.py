import os
import json
from tqdm import tqdm


def extract_links():
    save_path = '../saves/json/'
    models = sorted(os.listdir(save_path), key=lambda x: int(x))
    all_types = set()
    result = {}
    # https://civitai.com/api/download/models/62833
    for model in tqdm(models):
        if not os.path.exists(os.path.join(save_path, model, 'model.json')):
            print(f'warning: no model.json found in {model}')
            continue
        data = json.load(open(os.path.join(save_path, model, 'model.json')))
        if 'data' not in data:
            # print(f'warning: no valid data found in {model}/model.json')  # 404
            continue
        model_type = data['data']['type']
        all_types.add(model_type)
        if model_type not in result:
            result[model_type] = {}
        model_name = data['data']['name']
        model_link = f'https://civitai.com/models/{model}'
        model_key = f'{model_name} ~ {model_link}'
        result[model_type][model_key] = []
        for model_version in data['data']['modelVersions']:
            model_download_name = model_version['name']
            model_download_link = f"https://civitai.com/api/download/models/{model_version['id']}"
            result[model_type][model_key].append(f'{model_download_name} ~ {model_download_link}')
    json.dump(result, open('all_links.json', 'w'), indent=4, ensure_ascii=False, sort_keys=False)
    json.dump(list(all_types), open('all_types.json', 'w'), indent=4, ensure_ascii=False, sort_keys=True)


def extract_type_links(links, type='LORA'):
    result = {}
    count = len(links[type])
    result['models'] = links[type]
    result['meta'] = {}
    result['meta']['count'] = count
    json.dump(result, open(f'./{type}_links.json', 'w'), indent=4, ensure_ascii=False, sort_keys=True)


if __name__ == '__main__':
    # extract_links()
    types = json.load(open('./all_types.json'))
    links = json.load(open('./all_links.json'))
    for type in types:
        extract_type_links(links, type)