from typing import List, Callable, Dict, Iterable

from .log import get_logger
from .defs import (
    RecursiveDictStr2Callable,
    RobustOptionalFuncArgsTuple,
    OptionalFuncArgsTuple
)


class RootType():
    @staticmethod
    def _parse_func_arg_tuple(
        func_arg_tuple: RobustOptionalFuncArgsTuple
    ) -> OptionalFuncArgsTuple:
        if not isinstance(func_arg_tuple, tuple):
            func_arg_tuple = (func_arg_tuple,)
        if len(func_arg_tuple) == 2:
            func, arg = func_arg_tuple
            arg = arg or []
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
        func_name_path: Iterable[str] | Callable,
        all_supported_funcs: RecursiveDictStr2Callable,
        note: str
    ):
        if callable(func_name_path):
            return func_name_path
        if isinstance(func_name_path, str):
            func_name_path = (func_name_path,)
        now_supported_funcs = all_supported_funcs
        func_name_path_repr = '.'.join(func_name_path)
        for func_name in func_name_path:
            if func_name not in now_supported_funcs:
                raise ValueError(f"{note} {repr(func_name_path_repr)} not supported, supported {note}s are {repr(list(now_supported_funcs.keys()))}.")
            now_supported_funcs = now_supported_funcs[func_name]
        if not callable(now_supported_funcs):
            raise ValueError(f"{repr(func_name_path_repr)} is not a valid {note}.")
        return now_supported_funcs

    def __init__(self):
        pass
    
    def _get_logger(self, name=None):
        name = name or getattr(self, '_name', None)
        if name:
            name = '.'.join([__name__, self.__class__.__name__, name])
        else:
            name = '.'.join([__name__, self.__class__.__name__])
        self._logger = get_logger(name)
    
    def __repr__(self):
        return f'{repr(self.__class__.__qualname__)}'