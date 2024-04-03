import os
import json
from typing import Dict, Any, List

from ..utils.ds import AttrDict
from ..utils.cls import RootType
from ..utils.defs import (
    UNVISITED,
    VISITING,
    VISITED,
    RobustOptionalFuncArgsTuple,
    ArgGroup_logger_enable_file_handler,
)
from ..utils.log import get_logger

from .arg import *
from .arg import ArgSetter
# from .arg import ArgKeeper

__all__ = [
    'RequestArgGroup',
    'ItemArgGroup',
    'RequestorArgs',
    'SessionArgs',
    'StatusCodeMiddlewareArgs',
    'BasicMiddlewareArgs',
    'JSONSaverMiddlewareArgs',
    'ResultSaverMiddlewareArgs',
    'ContentSaverMiddlewareArgs',
    'StreamDownloaderMiddlewareArgs',
    'TextSaverMiddlewareArgs',
    'RequestsSessionArgs',
    'AioHTTPSessionArgs',
    'AsksSessionArgs',
]

logger = get_logger(__name__)
logger.info(f"importing module {__name__}")


class ArgsMeta(type):
    keyword = ['_defined_args', '_required_args']

    def __new__(cls, clsname, bases, attrs):
        for name, val in attrs.items():
            if name not in cls.keyword:
                continue
            if isinstance(val, dict):
                inherited = {}
                for base in bases:
                    if hasattr(base, name):
                        inherited.update(getattr(base, name))
                inherited.update(val)
            elif isinstance(val, list):
                inherited = []
                for base in bases:
                    if hasattr(base, name):
                        inherited += getattr(base, name)
                inherited += val
            else:
                continue
            attrs[name] = inherited
        return super().__new__(cls, clsname, bases, attrs)


class Args(AttrDict, RootType, metaclass=ArgsMeta):
    _name: str = 'args'
    
    _defined_args: AttrDict = AttrDict()    # SUBCLASS, define args in this group, str as arg name, ArgSetter as default for this arg
    _required_args: List[str] = []          # SUBCLASS, required args
    
    def __init__(
        self,
        args: Any,
    ):
        _args = {}
        Args._get_logger(__name__, level='debug', propagate=False)
        for arg in args:
            if arg not in self._defined_args:
                self._logger.warning(f"arg {repr(arg)} not defined in {repr(self)}")
                continue
            _args[arg] = args[arg]
        for defined_arg in self._defined_args:
            if defined_arg not in _args:
                if defined_arg in self._required_args:
                    raise ValueError(f"required arg {repr(defined_arg)} not set in {repr(self)}")
                _args[defined_arg] = self._defined_args[defined_arg]
                self._logger.info(f"arg {repr(defined_arg)} not set, using default {repr(self._defined_args[defined_arg])}")
        super().__init__(_args)
        
    def __repr__(self):
        return f'{repr(self.__class__.__qualname__)}({repr({key: value for key, value in self.items() if key in self._defined_args})})'


class ArgGroup(RootType):
    _name: str = 'arggroup'
    
    _defined_args: Dict[str, ArgSetter] = {}  # SUBCLASS, define args in this group, str as arg name, ArgSetter as default for this arg
    
    def __init__(
        self,
        args: ArgSetter | RobustOptionalFuncArgsTuple,
    ):
        """
            Set `ArgSetter` for defined args in this group, will use default if not.
        """
        super().__init__()
        self._args = {}  # must set `eslf._args` before calling `self._get_logger` because the latter will call `self.__getattr__` to get `self._name` args
        ArgGroup._get_logger(__name__, level='debug', propagate=False, add_file_handler=ArgGroup_logger_enable_file_handler)
        for arg in args:
            if arg not in self._defined_args:
                self._logger.warning(f"arg {repr(arg)} not defined in {repr(self)}")
                continue
            if not isinstance(args[arg], ArgSetter):
                args[arg] = self._defined_args[arg].__class__(args[arg])  # no need to pass in instantiated `ArgSetter`s
            if args[arg].__class__ != self._defined_args[arg].__class__:
                self._logger.warning(f"arg {repr(arg)} type mismatch, expected {repr(self._defined_args[arg])}, got {repr(args[arg])}")
                continue
            self._args[arg] = args[arg]
        for defined_arg in self._defined_args:
            if defined_arg not in self._args:
                self._args[defined_arg] = self._defined_args[defined_arg]
                self._logger.info(f"arg {repr(defined_arg)} not set, using default {repr(self._defined_args[defined_arg])}")
    
    def __call__(self, id, *extra_args, **extra_kwargs):
        """
            Call `ArgSetter`s in this group, attention is needed that some setter will use the value of other args, which introduces specific order of calling setters.
            
            Because we cannot explicitly detect if a setter will use the value of other args other than calling it, so we decide to use DFS-like method to traverse the graph of dependencies, and record the visiting status of each arg. This can be implemented by defining `self.__getattr__` for the args. In this way we can test if there is a loop in the graph easily, and if there is, error will be raised.
            
            Also, generate an order in advance is impossible, because the order may not be fixed across calls with different `id`s. This seems to bring some computation overhead, but in fact they are the same.
        """
        self._id = id
        self._extra_args = extra_args
        self._extra_kwargs = extra_kwargs
        self._status = {}
        self._path = []  # record possible current loop
        self._args_value = {}
        for arg in self._args:
            if arg not in self._status:
                self._path = []
                self.__getattr__(arg)
        return self._args_value

    def __getattr__(self, arg):
        """
            Return the value of arg `name`, if it is not set, call its setter and return the value. This is a tricky implement which should not be called by user, and is only intended to be called when calling `__call__` to set args.

            ~ A key difference between `__getattr__` and `__getattribute__` is that `__getattr__` is only invoked if the attribute wasn't found the usual ways. It's good for implementing a fallback for missing attributes, and is probably the one of two you want. `__getattribute__` is invoked before looking at the actual attributes on the object, and so can be tricky to implement correctly. You can end up in infinite recursions very easily.
        """
        if arg not in self._args:
            raise AttributeError(f"arg {repr(arg)} is not defined in {repr(self)}")
        if arg not in self._status:
            self._status[arg] = UNVISITED
        if self._status[arg] == UNVISITED:
            self._path.append(arg)
            self._status[arg] = VISITING
            self._args_value[arg] = self._args[arg](self._id, self, *self._extra_args, **self._extra_kwargs)  # call `ArgSetter` with (id: Any, arg_group: ArgGroup, *extra_args, **extra_kwargs)
            self._status[arg] = VISITED
        elif self._status[arg] == VISITING:
            self._path.append(arg)
            path_repr = " -> ".join([repr(arg) for arg in self._path])
            raise RuntimeError(f"loop detected when setting arg {repr(arg)} in {repr(self)}\npath: {path_repr}")
        elif self._status[arg] == VISITED:
            pass
        else:
            path_repr = " -> ".join([repr(arg) for arg in self._path])
            raise RuntimeError(f"unknown status {repr(self._status[arg])} when setting arg {repr(arg)} in {repr(self)}\npath: {path_repr}")
        return self._args_value[arg]
    

class _Args(Args):
    _defined_args: AttrDict = AttrDict({
    })
    _required_args: List[str] = []
    

class MiddlewareArgs(Args):
    pass
    
    
class StatusCodeMiddlewareArgs(MiddlewareArgs):
    _defined_args: AttrDict = AttrDict({
        'expected_status_codes': [200],
    })
    _required_args: List[str] = []


class BasicMiddlewareArgs(MiddlewareArgs):
    _defined_args: AttrDict = AttrDict({
        'reject_types': [],
    })
    _required_args: List[str] = []


class JSONSaverMiddlewareArgs(MiddlewareArgs):
    pass


class TextSaverMiddlewareArgs(MiddlewareArgs):
    pass


class StreamDownloaderMiddlewareArgs(MiddlewareArgs):
    pass


class ResultSaverMiddlewareArgs(MiddlewareArgs):
    pass


class ContentSaverMiddlewareArgs(MiddlewareArgs):
    pass


class SessionArgs(Args):
    _defined_args: AttrDict = AttrDict({
        'lib': None,
        'no_session': False,
        'cookies': {},
        'proxies': {},  # example: {'http': 'foo.bar:3128', 'http://host.name': 'foo.bar:4012'}
        'headers': {},
        'timeout': 60,
    })
    _required_args: List[str] = ['lib']


class RequestsSessionArgs(SessionArgs):
    _defined_args: AttrDict = AttrDict({
        'stream': False,
    })
    _required_args: List[str] = []


class AioHTTPSessionArgs(SessionArgs):
    _defined_args: AttrDict = AttrDict({
        'chunked_size': None,
    })
    _required_args: List[str] = []


class AsksSessionArgs(SessionArgs):
    pass


class RequestorArgs(Args):
    _defined_args: AttrDict = AttrDict({
        'nproc': 1,
        'async_sema': 1,
        'report_step': 100,
        'wait_timeout': 20,
        'wait_sleep': 2,
    })
    _required_args: List[str] = []


class _ArgGroup(ArgGroup):
    _defined_args: Dict[str, ArgSetter] = {
    }


class RequestArgGroup(ArgGroup):
    _defined_args: Dict[str, ArgSetter] = {
        'method': MethodSetter(('fixed', 'get')),
        'url': URLSetter('not_set'),                # `url`         is required, not set will raise error
        'referer': RefererSetter('host'),           # `referer`     is default to host of `url`
        'cookies': CookiesSetter(('fixed', {})),      # `cookies`     default to empty dict
        'params': ParamsSetter('none'),             # `params`      default to None
        'payload': PayloadSetter('none'),           # `payload`     default to None
        'proxies': ProxiesSetter(('fixed', {})),           # `proxies`     default to None
        'user_agent': UserAgentSetter('random'),    # `user-agent`  is randomly set by convention
        'headers': HeadersSetter('switch'),         # `headers`     can switch to different headers templates
        'stream': StreamSetter(('fixed', False)),     # `stream`      default to False
        'is_leaf': IsLeafSetter(('fixed', False)),
        'retry_limit': RetryLimitSetter(('fixed', 0)),
        'timeout': TimeoutSetter(('fixed', 60)),
    }


class ItemArgGroup(ArgGroup):
    _defined_args: Dict[str, ArgSetter] = {
        'save_dir': SaveDirSetter('not_set'),       # `save_dir`    is required, not set will raise error
        'bloodline': BloodlineSetter('inherit'),    # `bloodline`   is required, not set will raise error
    }


# ------------------------------------ Module Postprocess ------------------------------------ #

def _module_postprocess():
    module_report = {}
    for var_name, var_value in globals().items():
        if var_name in __all__:
            module_report[repr(var_value.__qualname__)] = {name: repr(setter) for name, setter in var_value._defined_args.items()}
    logger.debug(f"module {__name__} loaded:\n{json.dumps(module_report, indent=4, ensure_ascii=False)}\n")
    module_ref_path = 'docs/refs'
    if not os.path.exists(module_ref_path):
        os.makedirs(module_ref_path)
    with open(os.path.join(module_ref_path, f'{__name__}.json'), 'w') as f:
        json.dump(module_report, f, indent=4, ensure_ascii=False)

_module_postprocess()
logger.info(f"module {__name__} imported")