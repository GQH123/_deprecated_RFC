import io
import os
import sys
import json
import time
import pickle
import inspect
import functools
# from string import Formatter
from datetime import datetime
from RFC.utils.exception_utils import ParamTypeError, ParamError


def get_prev_module_name(level=2):
    try:
        return inspect.getmodule(inspect.stack()[level][0]).__name__
    except Exception:
        return '<unknown>'


def _parse_fileIO(file, from_module=None):
    if from_module is None:
        from_module = get_prev_module_name(2)
    if isinstance(file, io.IOBase) or file is output_channels:
        return file
    if isinstance(file, str):
        return open(file, 'w')
    raise ParamTypeError('file', file, [io.IOBase, str], from_module)


def init_output_channels():
    global output_channels
    output_channels = {}
    output_channels['stdout'] = (sys.stdout, True)


init_output_channels()


def update_output_channels(new_channels, from_module=None):
    if from_module is None:
        from_module = get_prev_module_name(1)
    for channel in new_channels:
        if not isinstance(channel, str):
            raise ParamTypeError('channel', channel, [str], from_module)
        if not isinstance(new_channels[channel], tuple):
            raise ParamTypeError('new_channels[channel]', new_channels[channel], [tuple], from_module)
        if len(new_channels[channel]) != 2:
            raise ParamError(f"'new_channels[channel]' should be a tuple with exactly 2 elements, but found {repr(new_channels[channel])}.", from_module)
        if not isinstance(new_channels[channel][1], bool):
            raise ParamTypeError('new_channels[channel][1]', new_channels[channel][1], [bool], from_module)
        new_channels[channel] = (_parse_fileIO(new_channels[channel][0]), new_channels[channel][1])

    output_channels.update(new_channels)


def switch_output_channel(channel, state, from_module=None):
    if from_module is None:
        from_module = get_prev_module_name(1)
    if channel not in output_channels:
        log(f'output channel {repr(channel)} is not found, nothing changed.', mode='warn', from_module=from_module)
        return
    if not isinstance(state, bool):
        raise ParamTypeError('state', state, [bool], from_module)
    output_channels[channel] = (output_channels[channel][0], state)


def log(message, file=output_channels, note='', mode='info', if_print=False, from_module=None, pure_output=False, end='\n'):
    if file is None:
        return
    from_module = get_prev_module_name(1) if from_module is None else from_module
    file = _parse_fileIO(file, from_module)
    current_time = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    if note:
        note = f'({note}) '
    if mode != 'info':
        from_module = ' (from ' + from_module + ')'
    else:
        from_module = ''

    mode = f'[{mode.upper()}] '
    result = current_time + note + mode + message + from_module

    if pure_output:
        result = message

    def print_with_file(file):
        nonlocal if_print
        if file is sys.stdout:
            if_print = False
        print(result, file=file, flush=True, end=end)
        if if_print:
            print(result, flush=True, end=end)

    if file is output_channels:
        for channel in file:
            if file[channel][1]:
                print_with_file(file[channel][0])
    else:
        print_with_file(file)


def retry(log_file, retry_times='forever', sleep_time=5, **kwargs):  # used only in manager class
    if retry_times == 'forever':
        retry_times = -1

    note = kwargs.get('note', '')
    mode = kwargs.get('mode', 'warning')
    from_module = kwargs.get('from_module', get_prev_module_name(1))

    def returned_func(func):
        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            nonlocal retry_times
            while retry_times != 0:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    log(message=f'retrying({retry_times}), <{type(e)}> {e}', file=log_file, note=note, mode=mode, from_module=from_module)
                    retry_times = retry_times-1 if retry_times > 0 else retry_times
                    time.sleep(sleep_time)
        return wrapped_func
    return returned_func


"""
def fill_format_str(s, **kwargs):
    def _parse_format_str_keys(s):
        return list(set([i[1] for i in Formatter().parse(s) if i[1] is not None]))

    keys = _parse_format_str_keys(s)
    for key in keys:
        if key not in kwargs:
            missing_param(key, inspect.getmodule(inspect.stack()[1][0]).__name__)
    return s.format(**kwargs)
"""


def check_fileIO(f):
    return isinstance(f, io.IOBase)


def pretty_print_parser(obj):
    if isinstance(obj, dict):
        return json.dumps(obj, sort_keys=True, indent=4)
    else:
        raise ParamTypeError('obj', obj, [dict], __name__)


def pretty_print(obj, **kwargs):
    print(pretty_print_parser(obj), **kwargs)


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


class BaseConfig:
    ...