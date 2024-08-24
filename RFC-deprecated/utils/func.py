import os
import json
import time
import pickle
import inspect
from typing import Optional, Any
from functools import wraps
import traceback

__all__ = [
    'retry',
    'save_object',
    'load_object',
    'get_prev_module_name',
]


def get_prev_module_name(
    level: int,
) -> str:
    try:
        frame = inspect.getmodule(inspect.stack()[level][0])
        assert frame is not None
        return frame.__name__
    except Exception:
        return '<unknown>'


def retry(
    retry_times: int = -1,
    default_return: Optional[Any] = None,  # note that Optional[Any] is different from Any, refer to https://github.com/python/mypy/issues/3138 for more detailed discussion
    sleep_time: Optional[float] = 0,
    raise_exception: bool = False,
    verbose: bool = True,
):
    if retry_times is None:
        retry_times = -1
    assert isinstance(retry_times, int) and retry_times >= -1
    if sleep_time is None:
        sleep_time = 0
    assert isinstance(sleep_time, float) and sleep_time >= 0
    def decorator(wrapped):
        @wraps(wrapped)
        def wrapper(*args, **kwargs):
            retry_time = 0
            st_time = time.time()
            while True:
                try:
                    st_time = time.time()
                    result = wrapped(*args, **kwargs)
                    ed_time = time.time()
                    return result
                except Exception as e:
                    if isinstance(e, NotImplementedError):
                        raise e
                    ed_time = time.time()
                    if verbose:
                        print(f'exception raised when calling {repr(wrapped.__name__)} (executed for {ed_time - st_time:.2f}s), retrying {retry_time}/{retry_times if retry_times != -1 else "inf"}, exception details: {repr(e)}')
                    if retry_times != -1:
                        retry_time += 1
                        if retry_time > retry_times:
                            if verbose:
                                print(f'\n{traceback.format_exc()}')
                                # traceback.print_exc()
                            if raise_exception:
                                assert False, f"too many retries, execution failed"
                            else:
                                if verbose:
                                    print(f"too many retries, return default\n")
                                return default_return
                    time.sleep(sleep_time)
        @wraps(wrapped)
        async def wrapper_async(*args, **kwargs):
            retry_time = 0
            st_time = time.time()
            while True:
                try:
                    st_time = time.time()
                    result = await wrapped(*args, **kwargs)
                    ed_time = time.time()
                    return result
                except Exception as e:
                    if isinstance(e, NotImplementedError):
                        raise e
                    ed_time = time.time()
                    if verbose:
                        print(f'exception raised when calling {repr(wrapped.__name__)} (executed for {ed_time - st_time:.2f}s), retrying {retry_time}/{retry_times if retry_times != -1 else "inf"}, exception details: {repr(e)}')
                    if retry_times != -1:
                        retry_time += 1
                        if retry_time > retry_times:
                            if verbose:
                                print(f'\n{traceback.format_exc()}')
                                # traceback.print_exc()
                            if raise_exception:
                                assert False, f"too many retries, execution failed"
                            else:
                                if verbose:
                                    print(f"too many retries, return default\n")
                                return default_return
                    time.sleep(sleep_time)
        return wrapper_async if inspect.iscoroutinefunction(wrapped) else wrapper
    return decorator


def _parse_mode(obj, path, mode, logger):
    all_supported_modes = ['auto', 'binary', 'text', 'json', 'pickle', 'pkl']
    if mode not in all_supported_modes:
        raise ValueError(f"unsupported mode {mode}, supported modes are {all_supported_modes}")
    if mode != 'auto':
        return mode
    filename = os.path.split(path)[-1]
    if filename == '':
        raise ValueError("filename not specified")
    ext = filename.split('.')[-1] if '.' in filename else ''
    if ext in ['json']:
        mode = 'json'
    elif ext in ['pkl', 'pickle']:
        mode = 'pickle'
    elif (obj is not None and isinstance(obj, str)) or (ext in ['txt', 'html', 'py', 'c', 'cpp', 'htm', 'js', 'css', 'ipynb', ]):
        mode = 'text'
    elif (obj is not None and isinstance(obj, bytes)) or (obj is None):
        mode = 'binary'
    else:
        if logger is not None:
            logger.warning(f"cannot auto detect mode for {repr(obj)}, using binary mode")
        mode = 'binary'
    return mode


class RobustJSONEncoder(json.JSONEncoder):
    def default(self, x):
        if inspect.isfunction(x):
            return x.__name__ + str(inspect.signature(x))
        elif hasattr(x, '__dict__') and (type(x).__name__ not in dir(__builtins__)):
            try:
                return json.JSONEncoder.default(self, x.__dict__)
            except:
                return self.default(x.__dict__)
        else:
            try:
                return json.JSONEncoder.default(self, x)
            except:
                return repr(x)


def save_object(obj, path, mode='auto', logger=None, raise_exception=False):
    def save_json():
        json.dump(obj, open(path, 'w'), ensure_ascii=False, indent=4, cls=RobustJSONEncoder)

    def save_pickle():
        pickle.dump(obj, open(path, 'wb'))

    def save_text():
        with open(path, 'w') as f:
            f.write(obj)

    def save_binary():
        with open(path, 'wb') as f:
            f.write(obj)

    try:
        dir_path = os.path.split(path)[0]
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        mode = _parse_mode(obj, path, mode, logger)
        if mode == 'json':
            save_json()
        elif mode == 'pickle' or mode == 'pkl':
            save_pickle()
        elif mode == 'text':
            try:
                return save_text()
            except TypeError:
                if logger is not None:
                    logger.warning(f"cannot save text file {repr(path)} as text, trying to save as binary")
                return save_binary()
        elif mode == 'binary':
            save_binary()
        else:
            raise ValueError(f"unknown mode {repr(mode)}")
    except Exception as e:
        if raise_exception:
            raise e
        else:
            if logger is not None:
                error_report = f'[{repr(type(e).__name__)}] {repr(e)}\n{traceback.format_exc()}'
                logger.warning(f"failed to save {repr(obj)} with mode {repr(mode)} to {repr(path)}, caught exception {repr(error_report)}")


def load_object(path, mode='auto', logger=None, default_return=None, raise_exception=False) -> object:
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

    try:
        mode = _parse_mode(None, path, mode, logger)
        if mode == 'json':
            return load_json()
        elif mode == 'pickle' or mode == 'pkl':
            return load_pickle()
        elif mode == 'text':
            try:
                return load_text()
            except UnicodeDecodeError:
                if logger is not None:
                    logger.warning(f"cannot load text file {repr(path)} as text, trying to load as binary")
                return load_binary()
        elif mode == 'binary':
            return load_binary()
        else:
            raise ValueError(f"unknown mode {repr(mode)}")
    except Exception as e:
        if raise_exception:
            raise e
        else:
            if logger is not None:
                error_report = f'[{repr(type(e).__name__)}] {repr(e)}'
                logger.warning(f"failed to load {repr(path)} with mode {repr(mode)}, caught exception {repr(error_report)}")
            return default_return