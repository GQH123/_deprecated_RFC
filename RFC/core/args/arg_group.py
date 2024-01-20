from typing import Callable, Any, Optional, Iterable, Tuple, Mapping, Dict

from RFC.core.utils.cls import RootType
from RFC.core.utils.log import get_logger
from RFC.core.utils.defs import (
    UNVISITED,
    VISITING,
    VISITED,
)
from RFC.core.utils.defs import allSupportedRequestLibsNames

from .arg_setter import *
from .arg_setter import ArgSetter

logger = get_logger(__name__)

class ArgGroup(RootType):
    _defined_args: Dict[str, ArgSetter] = {  # define args in this group, str as arg name, ArgSetter as default arg setter for this arg
    } # SUBCLASS
    
    def __init__(
        self,
        **args: Mapping[str, ArgSetter],
    ):
        """
            Set `ArgSetter` for defined args in this group, will use default if not.
        """
        super().__init__()
        self._args = {}
        for arg in args:
            if arg not in self._defined_args:
                logger.warning(f"arg {repr(arg)} not defined in {repr(self)}")
                continue
            if not isinstance(args[arg], ArgSetter):
                args[arg] = self._defined_args[arg].__class__(args[arg])  # no need to pass in instantiated `ArgSetter`s
            if type(args[arg]) != type(self._defined_args[arg]):
                logger.warning(f"arg {repr(arg)} type mismatch, expected {repr(self._defined_args[arg])}, got {repr(args[arg])}")
                continue
            self._args[arg] = args[arg]
        for defined_arg in self._defined_args:
            if defined_arg not in self._args:
                self._args[defined_arg] = self._defined_args[defined_arg]
                logger.info(f'arg {repr(defined_arg)} not set, using default {repr(self._defined_args[defined_arg])}')
    
    def __call__(self, id, request_lib):
        """
            Call `ArgSetter`s in this group, attention is needed that some setter will use the value of other args, which introduces specific order of calling setters.
            
            Because we cannot explicitly detect if a setter will use the value of other args other than calling it, so we decide to use DFS-like method to traverse the graph of dependencies, and record the visiting status of each arg. This can be implemented by defining `self.__getattr__` for the args. In this way we can test if there is a loop in the graph easily, and if there is, error will be raised.
            
            Also, generate an order in advance is impossible, because the order may not be fixed across calls with different `id`s. This seems to bring some computation overhead, but in fact they are the same.
        """
        self._id = id
        self._request_lib = request_lib
        self._status = {}
        self._path = []  # record possible current loop
        self._args_value = {}
        for arg in self._args:
            if arg not in self._status:
                self._path = []
                self._status[arg] = UNVISITED
                self.__getattr__(arg)
        return self._args_value
    # SUBCLASS

    def __getattr__(self, arg):
        """
            Return the value of arg `name`, if it is not set, call its setter and return the value. This is a tricky implement which should not be called by user, and is only intended to be called when calling `__call__` to set args.
            
            ~ A key difference between `__getattr__` and `__getattribute__` is that `__getattr__` is only invoked if the attribute wasn't found the usual ways. It's good for implementing a fallback for missing attributes, and is probably the one of two you want. `__getattribute__` is invoked before looking at the actual attributes on the object, and so can be tricky to implement correctly. You can end up in infinite recursions very easily.
        """
        if arg not in self._args:
            raise AttributeError(f"arg {repr(arg)} is not defined in {repr(self)}")
        if self._status[arg] == UNVISITED:
            self._path.append(arg)
            self._status[arg] = VISITING
            self._args_value[arg] = self._args[arg](self._id, self, self._request_lib)  # call `ArgSetter` with (id: Any, arg_group: Any, request_lib: str)
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

    def __repr__(self):
        return f'{repr(self.__class__.__qualname__)}'
    

class _ArgGroup(ArgGroup):
    _defined_args: Dict[str, ArgSetter] = {
    }
    def __call__(self, id, request_lib):
        arg_value = super().__call__(id, request_lib)
        request_param_kwargs = arg_value
        return request_param_kwargs


# to condense code, we ignore some python coding styles in the following part

class RequestArgGroup(ArgGroup):
    _defined_args: Dict[str, ArgSetter] = {
        'url': URLSetter('not_set'),                # `url`         is required, not set will raise error
        'referer': RefererSetter('host'),           # `referer`     is default to host of `url`
        'cookies': CookiesSetter('not_set'),        # `cookies`     should be set, but not required
        'params': ParamsSetter('none'),             # `params`      can be empty
        'payload': PayloadSetter('none'),           # `payload`     can be empty
        'proxies': ProxiesSetter('none'),           # `proxies`     can be empty
        'user-agent': UserAgentSetter('random'),    # `user-agent`  is randomly set by convention
        'headers': HeadersSetter('switch'),         # `headers`     can switch to different headers templates
    }
    def __call__(self, id, request_lib):
        arg_value = super().__call__(id, request_lib)
        if request_lib == 'requests':
            request_param_kwargs = {
                'url': arg_value['url'],
                'cookies': arg_value['cookies'],
                'params': arg_value['params'],
                'data': arg_value['payload'],
                'proxies': arg_value['proxies'],
                'headers': arg_value['headers'],
            }
        return request_param_kwargs

class ItemArgGroup(ArgGroup):
    _defined_args: Dict[str, ArgSetter] = {
        ...
    }