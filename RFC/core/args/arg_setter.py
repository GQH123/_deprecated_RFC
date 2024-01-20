import os
import json
from urllib.parse import urlparse
from fake_useragent import UserAgent
ua = UserAgent()

from typing import Callable, Any, Optional, Iterable, Tuple

from RFC.core.utils.cls import RootType
from RFC.core.utils.log import get_logger
from RFC.core.utils.defs import (
    Func,
    FuncName,
    OptionalFunc,
    FuncArgsTuple,
    OptionalFuncArgsTuple,
    RobustFuncArgsTuple,
    RobustOptionalFuncArgsTuple,
)
from RFC.core.utils.defs import allSupportedRequestLibsNames

logger = get_logger(__name__)

__all__ = [
    'URLSetter',
    'RefererSetter',
    'CookiesSetter',
    'ParamsSetter',
    'PayloadSetter',
    'ProxiesSetter',
    'UserAgentSetter',
    'HeadersSetter',
]


class ArgSetter(RootType):
    """
        `ArgSetter` is used to set value for an arg in `ArgGroup`. It is designed to be convenient for setting args for multiple `Item`s in one `Itemset`, so it in fact represents NOT the value, but the generating method of it. Actual value of args are attached to `Item`s.
        
        `ArgSetter` should only be used to instantiate `ArgGroup`.
    """
    _all_supported_casters = {
        'to': {
            'none': lambda x: x,
        },
        'from': {
            'none': lambda x: x,
        }
    } # SUBCLASS

    _all_supported_setters = {
        'fixed': lambda id, arg_group, value: value
    } # SUBCLASS

    @staticmethod
    def _parse_func_arg_tuple(
        func_arg_tuple: RobustFuncArgsTuple | RobustOptionalFuncArgsTuple
    ) -> FuncArgsTuple | OptionalFuncArgsTuple:
        if not isinstance(func_arg_tuple, tuple):
            func_arg_tuple = (func_arg_tuple, [])
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
        raise ValueError(f"func_arg_tuple {repr(func_arg_tuple)} is not valid.")

    def _get_caster_by_request_lib(self, request_lib: str) -> FuncName:
        """
            This method is used to get the name of `to_caster` function from the `<request_lib>`, which will be used in `__call__` method.
        """
        caster = 'none'
        logger.info(f'{repr(self)} get caster {repr(caster)} from request lib {repr(request_lib)}.')
        return caster
    # SUBCLASS

    def _get_caster_func(self, caster: OptionalFunc, to: bool) -> Callable:
        """
            This method is used to get the caster function from the `<caster>`, which may be a string specifying the caster name or already, a function.
        """
        if caster is None:
            caster = 'none'
        if not isinstance(caster, str):
            return caster
        mode = 'to' if to else 'from'
        if caster not in self._all_supported_casters[mode]:
            raise ValueError(f"{mode}_caster {repr(caster)} is not supported, supported {mode}_casters are {repr(list(self._all_supported_casters[mode].keys()))}.")
        return self._all_supported_casters[mode][caster]
    
    def _get_setter_func(self, setter: Func) -> Callable:
        """
            This method is used to get the setter function from the `<setter>`, which may be a string specifying the setter name or already, a function.
        """
        if setter is None:
            raise ValueError(f"setter cannot be None.")
        if not isinstance(setter, str):
            return setter
        if setter not in self._all_supported_setters:
            raise ValueError(f"setter {repr(setter)} is not supported, supported setters are {repr(list(self._all_supported_setters.keys()))}.")
        return self._all_supported_setters[setter]

    def __init__(
        self,
        setter: RobustFuncArgsTuple,
        caster: RobustOptionalFuncArgsTuple = (None, []),
    ):
        """
            `<setter>`: 
                `<setter>` is used to set value, which may be a direct value or a function which accepts `<id>` and `<arg_group>` for setting different `Item`s in an `Itemset` with flexible references to other args in corresponding `ArgGroup`.

            `<caster>`:
                `<caster>` is used to convert value to different types/formats. An `ArgSetter` class should support at least the `str` type. Will be called only after generating value from `<setter>`.
                
                `<caster>` has two types, `from_caster` and `to_caster`. `from_caster` is used to cast value from `<setter>` to the inner type, `to_caster` is used to cast value from the inner type to other types.
                
                When initiating `ArgSetter`, user pass in a `from_caster`, and `to_caster` is determined by the `request_lib` when generating args for `Item`s.
                
                `<caster>` can be a string or a function which accepts `<value>` and returns `<casted_value>`.
        """
        super().__init__()
        logger.info(f'{repr(self)} initiated with setter {repr(setter)} and caster {repr(caster)}.')
        setter, self.setter_args = self._parse_func_arg_tuple(setter)
        caster, self.caster_args = self._parse_func_arg_tuple(caster)
        self.setter = self._get_setter_func(setter)
        self.caster = self._get_caster_func(caster, to=False)

    def cast(
        self,
        value: Any,
        from_caster: RobustOptionalFuncArgsTuple = (None, []),
        to_caster: RobustOptionalFuncArgsTuple = (None, [])
    ) -> Any:
        """
            This method is used to convert the value type by `<from_caster>` and `<to_caster>`.
        """
        from_caster, from_caster_args = self._parse_func_arg_tuple(from_caster)
        to_caster, to_caster_args = self._parse_func_arg_tuple(to_caster)
        from_caster = self._get_caster_func(from_caster, to=False)
        to_caster = self._get_caster_func(to_caster, to=True)
        return to_caster(from_caster(value, *from_caster_args), *to_caster_args)

    def __call__(self, id: Any, arg_group: Any, request_lib: str) -> Any:
        """
            This is used in ArgGroup for generating args for that group. Should not be called by user.
        """
        result = self.cast(self.setter(id, arg_group, *self.setter_args), (self.caster, self.caster_args), self._get_caster_by_request_lib(request_lib))
        logger.info(f'{repr(self)} called, result: {repr(result)}.')
        return result
    
    def __repr__(self):
        return f'{repr(self.__class__.__qualname__)}'


class _ArgSetter(ArgSetter):
    _all_supported_casters = {
        'to': {
            'none': lambda x: x,
        },
        'from': {
            'none': lambda x: x,
        }
    }
    _all_supported_setters = {
        'fixed': lambda id, arg_group, value: value
    }
    def _get_caster_by_request_lib(self, request_lib: str) -> FuncName:
        caster = 'none'
        logger.info(f'{repr(self)} get caster {repr(caster)} from request lib {repr(request_lib)}.')
        return caster


# to condense code, we ignore some python coding styles in the following part

class URLSetter(ArgSetter):
    _all_supported_casters = {
        'to': {
            'none': lambda x: x,
        },
        'from': {
            'none': lambda x: x,
        }
    }
    
    @staticmethod
    def _url_not_set(id, arg_group):
        raise ValueError(f"arg {repr('url')} not set in {repr(arg_group)}")
    
    _all_supported_setters = {
        'replace_id': lambda id, arg_group, template: template.format(id=id),
        'fixed': lambda id, arg_group, value: value,
        'not_set': _url_not_set,
    }
    def _get_caster_by_request_lib(self, request_lib: str) -> FuncName:
        caster = 'none'
        logger.info(f'{repr(self)} get caster {repr(caster)} from request lib {repr(request_lib)}.')
        return caster

class RefererSetter(ArgSetter):
    _all_supported_casters = {
        'to': {
            'none': lambda x: x,
        },
        'from': {
            'none': lambda x: x,
        }
    }
    _all_supported_setters = {
        'url': lambda id, arg_group: arg_group.url,
        'host': lambda id, arg_group: '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(arg_group.url)),
        'fixed': lambda id, arg_group, value: value
    }
    def _get_caster_by_request_lib(self, request_lib: str) -> FuncName:
        caster = 'none'
        logger.info(f'{repr(self)} get caster {repr(caster)} from request lib {repr(request_lib)}.')
        return caster

class CookiesSetter(ArgSetter):
    _all_supported_casters = {
        'to': {
            'none': lambda x: x,
        },
        'from': {
            'none': lambda x: x,
        }
    }
    
    @staticmethod
    def _cookies_not_set(id, arg_group):
        logger.warning(f"arg {repr('cookies')} not set in {repr(arg_group)}")
        
    @staticmethod
    def _read_from_file(id, arg_group, path, type='text', sep='; ', cont='=', id2rank=None):
        _supported_file_types = ['text', 'json']
        if type not in _supported_file_types:
            raise ValueError(f"cookies file type {repr(type)} not supported, supported types are {repr(_supported_file_types)}.")
        if not os.path.exists(path):
            raise FileNotFoundError(f"cookies file {repr(path)} not found.")
        if id2rank is None:
            id2rank = lambda id: 0
        if type == 'text':
            with open(path, 'r') as f:
                cookies = [cookies for cookies in f.read().split(sep) if cookies]
            cookies = {k_v.split(cont)[0]: cont.join(k_v.split(cont)[1:]) for k_v in cookies}
        elif type == 'json':
            with open(path, 'r') as f:
                cookies = json.load(f)
        cookies = cookies[id2rank(id)]
        return cookies

    _all_supported_setters = {
        'fixed': lambda id, arg_group, value: value,
        'not_set': _cookies_not_set,
        'file': _read_from_file,
    }
    def _get_caster_by_request_lib(self, request_lib: str) -> FuncName:
        caster = 'none'
        logger.info(f'{repr(self)} get caster {repr(caster)} from request lib {repr(request_lib)}.')
        return caster

class ParamsSetter(ArgSetter):
    _all_supported_casters = {
        'to': {
            'none': lambda x: x,
        },
        'from': {
            'none': lambda x: x,
        }
    }
    _all_supported_setters = {
        'fixed': lambda id, arg_group, value: value,
        'none': lambda id, arg_group: '',
    }
    def _get_caster_by_request_lib(self, request_lib: str) -> FuncName:
        caster = 'none'
        logger.info(f'{repr(self)} get caster {repr(caster)} from request lib {repr(request_lib)}.')
        return caster

class PayloadSetter(ArgSetter):
    _all_supported_casters = {
        'to': {
            'none': lambda x: x,
        },
        'from': {
            'none': lambda x: x,
        }
    }
    _all_supported_setters = {
        'fixed': lambda id, arg_group, value: value,
        'none': lambda id, arg_group: '',
    }
    def _get_caster_by_request_lib(self, request_lib: str) -> FuncName:
        caster = 'none'
        logger.info(f'{repr(self)} get caster {repr(caster)} from request lib {repr(request_lib)}.')
        return caster

class ProxiesSetter(ArgSetter):
    _all_supported_casters = {
        'to': {
            'none': lambda x: x,
        },
        'from': {
            'none': lambda x: x,
        }
    }
    _all_supported_setters = {
        'fixed': lambda id, arg_group, value: value,
        'none': lambda id, arg_group: '',
    }
    def _get_caster_by_request_lib(self, request_lib: str) -> FuncName:
        caster = 'none'
        logger.info(f'{repr(self)} get caster {repr(caster)} from request lib {repr(request_lib)}.')
        return caster

class UserAgentSetter(ArgSetter):
    _all_supported_casters = {
        'to': {
            'none': lambda x: x,
        },
        'from': {
            'none': lambda x: x,
        }
    }
    
    @staticmethod
    def _random(id, arg_group, type='random'):
        if type not in ua.browsers + ['random']:
            raise ValueError(f"user-agent random type {repr(type)} not supported, supported types are {repr(ua.browsers + ['random'])}.")
        return ua[type]
    
    _all_supported_setters = {
        'fixed': lambda id, arg_group, value: value,
        'random': _random,
    }
    def _get_caster_by_request_lib(self, request_lib: str) -> FuncName:
        caster = 'none'
        logger.info(f'{repr(self)} get caster {repr(caster)} from request lib {repr(request_lib)}.')
        return caster

class HeadersSetter(ArgSetter):
    _all_supported_casters = {
        'to': {
            'none': lambda x: x,
        },
        'from': {
            'none': lambda x: x,
        }
    }
    
    @staticmethod
    def _headers_not_set(id, arg_group):
        logger.warning(f"arg {repr('headers')} not set in {repr(arg_group)}")
        
    @staticmethod
    def _switch(id, arg_group, type='default'):
        options = {
            'default': {
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Sec-Fetch-Site': 'same-site',
                'Sec-Fetch-Mode': 'navigate',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7,en-GB;q=0.6,ru;q=0.5',
            },
        }
        if type not in options:
            raise ValueError(f"headers type {repr(type)} not supported, supported types are {repr(list(options.keys()))}.")
        return options[type]
    
    _all_supported_setters = {
        'fixed': lambda id, arg_group, value: value,
        'none': lambda id, arg_group: {},
        'not_set': _headers_not_set,
        'switch': _switch,
    }
    def _get_caster_by_request_lib(self, request_lib: str) -> FuncName:
        caster = 'none'
        logger.info(f'{repr(self)} get caster {repr(caster)} from request lib {repr(request_lib)}.')
        return caster