import os
import json
from tqdm import tqdm
from safetensors.torch import load_file


def check_dir(model_type='LoCon'):
    save_path = f'../../saves/models/{model_type}/'
    result = {}
    ext = {}
    models = os.listdir(save_path)
    for model in models:
        result[model] = {}
        model_versions = os.listdir(os.path.join(save_path, model))
        for model_version in model_versions:
            result[model][model_version] = []
            model_files = os.listdir(os.path.join(save_path, model, model_version))
            for model_file in model_files:
                if model_file in ['_result.pkl', '_item.pkl']:
                    continue
                if model_file.endswith('.bin'):
                    model_file = model_file[:-4]
                result[model][model_version].append(model_file)
                _ext = model_file.split('.')[-1]
                ext[_ext] = ext.get(_ext, 0) + 1
    json.dump(result, open(f'{model_type}_files.json', 'w'), indent=4, ensure_ascii=False, sort_keys=True)
    json.dump(ext, open(f'{model_type}_files_ext.json', 'w'), indent=4, ensure_ascii=False, sort_keys=True)


def load_model(model_type='LoCon'):
    save_path = f'../../saves/models/{model_type}/'
    models = os.listdir(save_path)
    result = {}
    keys = {}
    for model in tqdm(models):
        result[model] = {}
        model_versions = os.listdir(os.path.join(save_path, model))
        for model_version in model_versions:
            model_files = os.listdir(os.path.join(save_path, model, model_version))
            for model_file in model_files:
                if model_file in ['_result.pkl', '_item.pkl']:
                    continue
                _model_file = model_file
                if model_file.endswith('.bin'):
                    model_file = model_file[:-4]
                _ext = model_file.split('.')[-1]
                if _ext not in ['safetensors']:
                    continue
                try:
                    weights = load_file(os.path.join(save_path, model, model_version, _model_file), device='cpu')
                except Exception as e:
                    error_report = f'[{type(e).__name__}] {e}, {os.path.join(save_path, model, model_version, _model_file)}'
                    print(f'{error_report}')
                    continue
                result[model][model_version] = {k: str(tuple(weights[k].shape)) for k in weights}
                for k in weights:
                    if k not in keys:
                        keys[k] = set()
                    keys[k].add(str(tuple(weights[k].shape)))
    keys = {k: list(v) for k, v in keys.items()}
    json.dump(result, open(f'{model_type}_weights.json', 'w'), indent=4, ensure_ascii=False, sort_keys=True)
    json.dump(keys, open(f'{model_type}_weights_keys.json', 'w'), indent=4, ensure_ascii=False, sort_keys=True)


def get_key_list(model_type='LoCon'):
    keys = json.load(open(f'{model_type}_weights_keys.json'))
    keys_list = {k: [] for k in keys}
    json.dump(keys_list, open(f'{model_type}_weights_keys_list.json', 'w'), indent=4, ensure_ascii=False, sort_keys=True)


if __name__ == '__main__':
    # check_dir()
    load_model()
    # get_key_list()
    ...