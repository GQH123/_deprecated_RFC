import os
import sys
from logging.handlers import RotatingFileHandler
from logging import Logger
import logging
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


class LoggerWrapper:
    def __init__(self, logger, name, log_path):
        if not os.path.exists(log_path):
            os.makedirs(log_path, exist_ok=True)
        self.fp = os.path.join(log_path, name+'.log')
        with open(self.fp, 'w'):
            pass
        self.logger = logger
        
    # def lazy_init(self):
    #     self.fp = open(self.fp, 'w')
    #     if self.logger.handlers == []:
    #         _default_handler = logging.StreamHandler()
    #         _default_handler.flush = sys.stderr.flush
    #         self.logger.addHandler(_default_handler)

    def debug(self, msg, *args, **kwargs):
        with open(self.fp, 'a') as fp:
            _s = sys.stderr
            sys.stderr = fp
            self.logger.debug(msg, *args, **kwargs)
            sys.stderr = _s
    
    def info(self, msg, *args, **kwargs):
        with open(self.fp, 'a') as fp:
            _s = sys.stderr
            sys.stderr = fp
            self.logger.info(msg, *args, **kwargs)
            sys.stderr = _s
        
    def warn(self, msg, *args, **kwargs):
        self.warning(msg, *args, **kwargs)
        
    def warning(self, msg, *args, **kwargs):
        with open(self.fp, 'a') as fp:
            _s = sys.stderr
            sys.stderr = fp
            self.logger.warning(msg, *args, **kwargs)
            sys.stderr = _s
        
    def exception(self, msg, *args, **kwargs):
        self.error(msg, *args, **kwargs)
        
    def error(self, msg, *args, **kwargs):
        with open(self.fp, 'a') as fp:
            _s = sys.stderr
            sys.stderr = fp
            self.logger.error(msg, *args, **kwargs)
            sys.stderr = _s
        
    def fatal(self, msg, *args, **kwargs):
        self.critical(msg, *args, **kwargs)
        
    def critical(self, msg, *args, **kwargs):
        with open(self.fp, 'a') as fp:
            _s = sys.stderr
            sys.stderr = fp
            self.logger.critical(msg, *args, **kwargs)
            sys.stderr = _s
        
    # def close(self):
    #     self.fp.close()


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
        delay=True,
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
            cls._logger.addHandler(RotatingFileHandler(log_path, mode='w', encoding='utf-8', delay=delay, **RotatingFileHandler_config))
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
        delay=True,
        return_logger=False,
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
        _logger = get_logger(logger_name)
        _logger.setLevel(level)
        if add_file_handler:
            if log_path is None:
                log_path = './logs'
            log_path = os.path.join(log_path, name+'.log')
            log_dir = os.path.dirname(log_path)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            _logger.addHandler(RotatingFileHandler(log_path, mode='w', encoding='utf-8', delay=delay, **RotatingFileHandler_config))
        if enable_format:
            enable_explicit_format(_logger)
        _logger.propagate = propagate
        if return_logger:
            return _logger
        self._logger = _logger
    
    def __repr__(self):
        return f'{repr(self.__class__.__qualname__)}'