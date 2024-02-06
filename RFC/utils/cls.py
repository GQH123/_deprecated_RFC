import os
from logging.handlers import RotatingFileHandler
from typing import Callable, Iterable

from .log import (
    get_logger,
    enable_explicit_format,
    _get_library_name,
    log_levels,
    _default_log_level,
)
from .defs import (
    RecursiveDictStr2Callable,
    RobustOptionalFuncArgsTuple,
    OptionalFuncArgsTuple,
    RotatingFileHandler_config,
)

__all__ = [
    'RootType'
]


class RootType():
    @staticmethod
    def _parse_func_arg_tuple(
        func_arg_tuple: RobustOptionalFuncArgsTuple
    ) -> OptionalFuncArgsTuple:
        if not isinstance(func_arg_tuple, tuple):
            func_arg_tuple = (func_arg_tuple,)
        if len(func_arg_tuple) == 2:
            func, arg = func_arg_tuple
            # arg = arg or []
            if not isinstance(arg, list):
                arg = [arg]
            return func, arg
        if len(func_arg_tuple) == 0:
            return None, []
        if len(func_arg_tuple) == 1:
            return func_arg_tuple[0], []
        return func_arg_tuple[0], list(func_arg_tuple[1:])

    @staticmethod
    def _get_func_recursive(
        func_name_path: Iterable[str] | str,
        all_supported_funcs: RecursiveDictStr2Callable,
        note: str
    ):
        if isinstance(func_name_path, str):
            func_name_path = (func_name_path,)
        now_supported_funcs = all_supported_funcs
        func_name_path_repr = '.'.join(func_name_path)
        for func_name in func_name_path:
            if callable(now_supported_funcs):
                raise ValueError(f"{note} {repr(func_name_path_repr)} is not a valid {note}.")
            if func_name not in now_supported_funcs:
                raise ValueError(f"{note} {repr(func_name_path_repr)} not supported, supported {note}s are {repr(list(now_supported_funcs.keys()))}.")
            now_supported_funcs = now_supported_funcs[func_name]
        if not callable(now_supported_funcs):
            raise ValueError(f"{repr(func_name_path_repr)} is not a valid {note}.")
        return now_supported_funcs

    def __init__(self):
        pass
    
    @classmethod
    def _get_logger(
        cls,
        prefix=None,
        name=None,
        log_path=None,
        add_file_handler=True,
        enable_format=True,
        level=_default_log_level,
        propagate=True,
    ):
        if getattr(cls, '_logger', None) is not None:
            # cls._logger.info(f"logger already exists in {repr(cls)}")
            return
        if isinstance(level, str):
            level = log_levels[level]
        if not isinstance(level, int):
            raise ValueError(f"level {repr(level)} is not a valid log level.")
        name = name or getattr(cls, '_name', None)
        if name is None:
            name_list = []
            if prefix is not None:
                name_list.append(prefix)
            name_list.append(cls.__name__)
            name = '.'.join(name_list)
        logger_name = name
        if not logger_name.startswith(_get_library_name()+'.'):
            logger_name = _get_library_name()+'.'+logger_name
        cls._logger = get_logger(logger_name)
        cls._logger.setLevel(level)
        if add_file_handler:
            if log_path is None:
                log_path = './logs'
            log_path = os.path.join(log_path, name+'.log')
            log_dir = os.path.dirname(log_path)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            cls._logger.addHandler(RotatingFileHandler(log_path, mode='w', encoding='utf-8', delay=True, **RotatingFileHandler_config))
        if enable_format:
            enable_explicit_format(cls._logger)
        cls._logger.propagate = propagate
    
    def _get_logger_self(
        self,
        prefix=None,
        name=None,
        log_path=None,
        add_file_handler=True,
        enable_format=True,
        level=_default_log_level,
        propagate=True,
    ):
        if isinstance(level, str):
            level = log_levels[level]
        if not isinstance(level, int):
            raise ValueError(f"level {repr(level)} is not a valid log level.")
        name = name or getattr(self, '_name', None)
        if name is None:
            name_list = []
            if prefix is not None:
                name_list.append(prefix)
            name_list.append(self.__class__.__name__)
            name = '.'.join(name_list)
        logger_name = name
        if not logger_name.startswith(_get_library_name()+'.'):
            logger_name = _get_library_name()+'.'+logger_name
        self._logger = get_logger(logger_name)
        self._logger.setLevel(level)
        if add_file_handler:
            if log_path is None:
                log_path = './logs'
            log_path = os.path.join(log_path, name+'.log')
            log_dir = os.path.dirname(log_path)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            self._logger.addHandler(RotatingFileHandler(log_path, mode='w', encoding='utf-8', delay=True, **RotatingFileHandler_config))
        if enable_format:
            enable_explicit_format(self._logger)
        self._logger.propagate = propagate
    
    def __repr__(self):
        return f'{repr(self.__class__.__qualname__)}'