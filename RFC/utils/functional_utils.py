import io
import os
import sys
import json
import time
import pickle
import inspect
import builtins
import functools
import traceback
from typing import Any
from functools import partial
# from string import Formatter
from datetime import datetime
from dataclasses import dataclass, field

from RFC.utils.exception_utils import SavingError, ParamTypeError, ParamError, ParamValueError, FileNotFoundError, FileFormatError, ParamSettingError


def get_prev_module_name(
    level: int = 2,
) -> str:
    try:
        frame = inspect.getmodule(inspect.stack()[level][0])
        assert frame is not None
        return frame.__name__
    except Exception:
        return '<unknown>'


def init_global_project_config(project_config):
    global global_project_config
    global_project_config = project_config  # need to be modified


def get_project_prefix(prefix='root', from_module=None):
    if from_module is None:
        from_module = get_prev_module_name(2)
    all_supported_prefix = ['root', 'meta', 'result', 'log', 'raw', 'config', 'error']
    if prefix not in all_supported_prefix:
        raise ParamValueError('prefix', prefix, all_supported_prefix, from_module)
    if prefix == 'root':
        return global_project_config.project_root
    elif prefix == 'meta':
        return os.path.join(global_project_config.project_root, global_project_config.project_meta_path)
    elif prefix == 'result':
        return os.path.join(global_project_config.project_root, global_project_config.project_result_path)
    elif prefix == 'log':
        return os.path.join(global_project_config.project_root, global_project_config.project_log_path)
    elif prefix == 'config':
        return os.path.join(global_project_config.project_root, global_project_config.project_config_path)
    elif prefix == 'raw':
        return os.path.join(global_project_config.project_root, global_project_config.project_raw_path)
    elif prefix == 'error':
        return os.path.join(global_project_config.project_root, global_project_config.project_error_path)


def _parse_fileIO(file, from_module=None):
    if from_module is None:
        from_module = get_prev_module_name(2)
    if isinstance(file, io.IOBase):
        return file
    if isinstance(file, str):
        if file in output_channels:
            if isinstance(output_channels[file], partial):
                output_channels[file] = output_channels[file]()  # lazy open
            return output_channels[file]
        else:
            raise ParamValueError('file', file, list(output_channels.keys()), from_module)
    if isinstance(file, list):
        return [_parse_fileIO(f, from_module) for f in file]
    raise ParamTypeError('file', file, [io.IOBase, str], from_module)


def init_output_channels():
    global output_channels
    output_channels = {}
    output_channels['stdout'] = sys.stdout


init_output_channels()


def update_output_channels(channel_name, channel, prefix_project_dir='root', from_module='<unknown>'):
    if from_module is None:
        from_module = get_prev_module_name(1)
    if isinstance(channel, io.IOBase):
        output_channels[channel_name] = channel
    elif isinstance(channel, str):
        output_channels[channel_name] = partial(open, os.path.join(get_project_prefix(prefix_project_dir, from_module), channel), 'w')  # lazy open
    else:
        raise ParamTypeError('channel', channel, [io.IOBase, str], from_module)

def log(
    message: Any = '',
    file: Any = 'main',
    note: str = 'Log',
    mode: str = 'info',
    from_module: str | None = None,
    pure_output: bool = False,
    flush: bool = True,
    trace: bool = False,
    **kwargs,
):
    try:
        message = str(message)
    except Exception:
        message = repr(message)
    if file is None:
        return
    from_module = get_prev_module_name(1) if from_module is None else from_module
    file = _parse_fileIO(file, from_module)
    current_time = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    mode = f'[{mode.upper()}]'
    if trace:
        message += f'\nTraceback:\n{traceback.format_exc()}\n'
    if pure_output:
        result = message
    else:
        result = f'{current_time} ({note}, from {from_module}) {mode} {message}'

    def print_with_file(file):
        if file is None:
            return
        print(result, file=file, flush=flush, **kwargs)

    if not isinstance(file, list):
        file = [file]
    for channel in file:
        print_with_file(channel)


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
        return json.dumps(obj, sort_keys=True, indent=4, default=lambda x: x.__dict__ if hasattr(x, '__dict__') and (type(x).__name__ not in dir(builtins)) else str(x))
    else:
        raise ParamTypeError('obj', obj, [dict], __name__)


def pretty_print(obj, **kwargs):
    print(pretty_print_parser(obj), **kwargs)


def parse_restriction(x, args_name, from_module):
    """ usage
        include = parse_restriction(self_kwargs['include'], 'include', __name__)
        exclude = parse_restriction(self_kwargs['exclude'], 'exclude', __name__)
    """
    match x:
        case 'all':
            x = True
        case 'none':
            x = []
        case None:
            x = []
        case x if all(isinstance(y, str) for y in x):
            x = x
        case _:
            raise ParamSettingError(f"Incorrect format of arg {args_name}", module_name=from_module, **{args_name: x})
    return x


def check_restriction(x, include, exclude):
    """ usage
        if not check_restriction(xxx_name, include, exclude):
            continue
    """
    if (include is True or x in include) and (exclude is not True and x not in exclude):
        return True
    else:
        return False


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


def save_object(obj, path, prefix_project_dir='root', mode='auto'):
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

    path = os.path.join(get_project_prefix(prefix_project_dir), path)
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
        # print(f'Saving {path} fails... [{type(e).__name__}], {e}')
        raise SavingError(obj, path, prefix_project_dir, mode, e)


def load_object(path, mode='auto', prefix_project_dir='root') -> object:
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

    path = os.path.join(get_project_prefix(prefix_project_dir), path)
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
        # print(f'Loading {path} fails, using default ... [{type(e).__name__}], {e}')
        raise e