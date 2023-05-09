import os
import json
import pickle


def _parse_mode(path, mode):
    if mode not in ['auto', 'binary', 'text', 'json', 'pickle']:
        raise ValueError(f"Unsupported mode {mode}")

    if mode != 'auto':
        return mode

    filename = os.path.split(path)[-1]
    if filename == '':
        raise ValueError("You must specify a file name")
    ext = filename.split('.')[-1] if '.' in filename else ''

    if ext in ['json']:
        mode = 'json'
    elif ext in ['pkl', 'pickle']:
        mode = 'pickle'
    elif ext in ['txt', 'html', 'py', 'c', 'cpp', 'htm']:
        mode = 'text'
    else:
        mode = 'binary'

    return mode


def save_object(obj, path, mode='auto'):
    def save_json():
        json.dump(obj, open(path, 'w'), ensure_ascii=False, indent=4)

    def save_pickle():
        pickle.dump(obj, open(path, 'wb'))

    def save_text():
        with open(path, 'w') as f:
            f.write(obj)

    def save_binary():
        with open(path, 'wb') as f:
            f.write(obj)

    dir_path = os.path.split(path)[0]
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    mode = _parse_mode(path, mode)

    try:
        if mode == 'json':
            save_json()
        elif mode == 'pickle' or mode == 'pkl':
            save_pickle()
        elif mode == 'text':
            save_text()
        elif mode == 'binary':
            save_binary()
        else:
            raise AssertionError(f"Unknown Error, mode: {mode}")
    except Exception as e:
        print(f'Saving {path} fails... [{type(e).__name__}], {e}')


def load_object(path, mode='auto', default=None):
    def load_json():
        return json.load(open(path, 'r'))

    def load_pickle():
        return pickle.load(open(path, 'rb'))

    def load_text():
        with open(path, 'r') as f:
            return f.read()

    def load_binary():
        with open(path, 'rb') as f:
            return f.read()

    mode = _parse_mode(path, mode)

    try:
        if mode == 'json':
            return load_json()
        elif mode == 'pickle' or mode == 'pkl':
            return load_pickle()
        elif mode == 'text':
            return load_text()
        elif mode == 'binary':
            return load_binary()
        else:
            raise AssertionError(f"Unknown Error, mode: {mode}")
    except Exception as e:
        print(f'Loading {path} fails, using default ... [{type(e).__name__}], {e}')
        return default