import os
import json
from urllib.parse import urlparse
from fake_useragent import UserAgent
ua = UserAgent()

from typing import Callable, Any, Optional

from ..utils.cls import RootType
from ..utils.defs import (
    OptionalFunc,
    RobustOptionalFuncArgsTuple,
    RecursiveDictStr2Callable,
)
from ..utils.log import get_logger
from ..utils.attr import get_func_param

__all__ = [
    'MethodSetter',
    'URLSetter',
    'RefererSetter',
    'CookiesSetter',
    'ParamsSetter',
    'PayloadSetter',
    'ProxiesSetter',
    'UserAgentSetter',
    'HeadersSetter',
    'StreamSetter',
    'SaveDirSetter',
    'BloodlineSetter',
]

logger = get_logger(__name__)
logger.info(f"importing module {__name__}")


class ArgRootTypeMeta(type):
    keyword_prefixes = ['_all_supported_']

    def __new__(cls, clsname, bases, attrs):
        for name, val in attrs.items():
            if not isinstance(val, dict):
                continue
            key_attr = False
            inherited_dict = {}
            for keyword_prefix in cls.keyword_prefixes:
                if name.startswith(keyword_prefix):
                    key_attr = True
                    break
            if not key_attr:
                continue
            for base in bases:
                if hasattr(base, name):
                    inherited_dict.update(getattr(base, name))
            inherited_dict.update(val)
            attrs[name] = inherited_dict
        return super().__new__(cls, clsname, bases, attrs)


class ArgRootType(RootType, metaclass=ArgRootTypeMeta):
    """
        `ArgRootType` implement some common methods for arg utilities.
        
        This is not intended to be used directly, but to be subclassed in different arg utilities.
    """
    def __init__(
        self,
    ):
        super().__init__()
        # self.__class__._get_logger(__name__)


"""
class ArgCaster(ArgRootType):
    \"""
        `ArgCaster` separate caster part of `ArgSetter` to make it simpler, and to implement other arg utilities more easily.
    \"""
    _all_supported_casters: RecursiveDictStr2Callable = {
        'to': {
            'none': lambda x: x,
        },
        'from': {
            'none': lambda x: x,
        }
    }
    # SUBCLASS
    
    @classmethod
    def _get_caster_func(cls, caster: OptionalFunc, to: bool) -> Callable:
        if callable(caster):
            return caster
        return cls._get_func_recursive(('to' if to else 'from', caster or 'none'), cls._all_supported_casters, "caster")
    
    def __init__(self):
        raise ValueError(f"{repr(self)} should not be instantiated")

    @classmethod
    def cast(
        cls,
        value: Any,
        from_caster: RobustOptionalFuncArgsTuple = None,
        to_caster: RobustOptionalFuncArgsTuple = None,
    ) -> Any:
        \"""
            `<caster>` is used to convert value to different types/formats, which has two types, `from_caster` and `to_caster`. `from_caster` is used to cast value from `<setter>` to the inner type, `to_caster` is used to cast value from the inner type to other types. `<caster>` can be a string or a function which accepts `<value>` and returns `<casted_value>`.
            
            This method is used to convert the value type by `<from_caster>` and `<to_caster>`.
        \"""
        if from_caster is not None:
            from_caster, from_caster_args = cls._parse_func_arg_tuple(from_caster)
            from_caster = cls._get_caster_func(from_caster, to=False)
            value = from_caster(value, *from_caster_args)
        if to_caster is not None:
            to_caster, to_caster_args = cls._parse_func_arg_tuple(to_caster)
            to_caster = cls._get_caster_func(to_caster, to=True)
            value = to_caster(value, *to_caster_args)
        return value
    
    
class _ArgCaster(ArgCaster):
    _all_supported_casters = {
        'to': {
            'none': lambda x: x,
        },
        'from': {
            'none': lambda x: x,
        }
    }
"""


class ArgSetter(ArgRootType):
    """
        `ArgSetter` is used to set value for an arg in `ArgGroup`. It is designed to be convenient for setting args for multiple `Item`s in one `Itemset`, so it in fact represents NOT the value, but the generating method of it. Actual value of args are attached to `Item`s.
        
        `ArgSetter` should only be used to instantiate `ArgGroup`.
    """
    _name: str = 'argsetter'

    @staticmethod
    def _not_set(id, arg_group, **kwargs):
        raise ValueError(f"arg {repr(kwargs['self'])} not set in {repr(arg_group)}")
        
    _all_supported_setters = {
        'fixed': lambda id, arg_group, value, **kwargs: value,
        'none': lambda id, arg_group, **kwargs: None,
        'not_set': _not_set,
        'replace_id': lambda id, arg_group, template, **kwargs: template.format(id=id),
    }
    # SUBCLASS

    def _get_setter_func(self, setter: OptionalFunc) -> Callable:
        if callable(setter):
            return setter
        return self._get_func_recursive(setter or 'none', self._all_supported_setters, "setter")

    def __init__(
        self,
        setter: RobustOptionalFuncArgsTuple = None,
    ):
        """
            `<setter>` is used to set value, which may be a direct value or a function which accepts `<id>` and `<arg_group>` for setting different `Item`s in an `Itemset` with flexible references to other args in corresponding `ArgGroup`.
        """
        super().__init__()
        ArgSetter._get_logger(__name__, level='debug', propagate=False)
        self._logger.debug(f"{self.__class__.__name__} initiated with setter tuple {repr(setter)}.")
        setter, self.setter_args = self._parse_func_arg_tuple(setter)
        self.setter = self._get_setter_func(setter)
        self._logger.debug(f"{repr(self)} parsed setter {repr(self.setter)} and setter args {repr(self.setter_args)}.")
        self._logger.debug(f"{repr(self)} initiated with setter {repr(setter)}.")

    def __call__(self, id: Any, arg_group: Any, *extra_args, **extra_kwargs) -> Any:
        """
            This is used in `ArgGroup` for generating args for that group. Should not be called by user.
        """
        result = self.setter(id, arg_group, *self.setter_args, *extra_args, self=self, **extra_kwargs)
        self._logger.debug(f"{repr(self)} called, result: {repr(result)}.")
        return result

    def __repr__(self):
        return f"{self.__class__.__name__}({self.setter.__qualname__}({', '.join([repr(args) for args in self.setter_args])}))"


class _ArgSetter(ArgSetter):
    _all_supported_setters = {
    }


"""
    `ArgSetter` should not need to know request_lib, which will mess up the operation logic of RFC.


class RequestArgSetter(ArgSetter):
    def _get_caster_by_request_lib(self, request_lib: str) -> FuncName:
        \"""
            This method is used to get the name of `to_caster` function from the `<request_lib>`, which will be used in `__call__` method.
        \"""
        caster = 'none'
        self._logger.debug(f"{repr(self)} get caster {repr(caster)} from request lib {repr(request_lib)}.")
        return caster
    # SUBCLASS
    
    def __init__(
        self,
        setter: RobustOptionalFuncArgsTuple = None,
        from_caster: RobustOptionalFuncArgsTuple = None,
    ):
        super().__init__(setter, from_caster)
    
    def __call__(self, id: Any, arg_group: Any, request_lib: str) -> Any:
        result = self.cast(self.setter(id, arg_group, *self.setter_args, self=self), to_caster=self._get_caster_by_request_lib(request_lib))
        self._logger.debug(f"{repr(self)} called, result: {repr(result)}.")
        return result


class _RequestArgSetter(RequestArgSetter):
    _all_supported_casters = {
        'to': {
            'none': lambda x: x,
        },
        'from': {
            'none': lambda x: x,
        }
    }
    _all_supported_setters = {
        'fixed': lambda id, arg_group, value, **kwargs: value,
        'none': lambda id, arg_group, **kwargs: None
    }
    def _get_caster_by_request_lib(self, request_lib: str) -> FuncName:
        caster = 'none'
        self._logger.debug(f"{repr(self)} get caster {repr(caster)} from request lib {repr(request_lib)}.")
        return caster
"""


class MethodSetter(ArgSetter):
    pass


class URLSetter(ArgSetter):
    pass


class RefererSetter(ArgSetter):
    _all_supported_setters = {
        'url': lambda id, arg_group, **kwargs: arg_group.url,
        'host': lambda id, arg_group, **kwargs: '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(arg_group.url)),
    }


class CookiesSetter(ArgSetter):
    @staticmethod
    def _read_from_file(id, arg_group, path, type='text', sep='; ', cont='=', id2rank: Optional[Callable[[Any], int]]=None, **kwargs):
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
            cookies = [{k_v.split(cont)[0]: cont.join(k_v.split(cont)[1:]) for k_v in _cookies} for _cookies in cookies]
        elif type == 'json':
            with open(path, 'r') as f:
                cookies = json.load(f)
                if not isinstance(cookies, list):
                    cookies = [cookies]
        else:
            raise ValueError(f"cookies file type {repr(type)} not supported, supported types are {repr(_supported_file_types)}.")
        cookies = cookies[id2rank(id)]
        return cookies

    _all_supported_setters = {
        'file': _read_from_file,
    }


class ParamsSetter(ArgSetter):
    pass


class PayloadSetter(ArgSetter):
    pass


class ProxiesSetter(ArgSetter):
    pass


class StreamSetter(ArgSetter):
    pass


class UserAgentSetter(ArgSetter):
    @staticmethod
    def _random(id, arg_group, type='random', **kwargs):
        if isinstance(ua.browsers, str):
            ua.browsers = [ua.browsers]
        if type not in ua.browsers + ['random']:
            raise ValueError(f"user-agent random type {repr(type)} not supported, supported types are {repr(ua.browsers + ['random'])}.")
        return ua[type]

    _all_supported_setters = {
        'random': _random,
    }


class HeadersSetter(ArgSetter):
    @staticmethod
    def _switch(id, arg_group, type='default', **kwargs):
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
        'switch': _switch,
    }


class SaveDirSetter(ArgSetter):
    @staticmethod
    def _auto(id, arg_group, prefix, sep, **kwargs):
        save_dir = os.path.join(prefix, sep.join([repr(item_id) for item_type_name, item_id in arg_group.bloodline]))
        return save_dir

    _all_supported_setters = {
        'auto': _auto,
    }


class BloodlineSetter(ArgSetter):
    @staticmethod
    def _inherit(id, arg_group, _bld=None, **kwargs):
        if _bld is None:
            _bld = []
        return _bld + [(kwargs['_item_type'], id)]

    _all_supported_setters = {
        'inherit': _inherit,
    }

"""
class ArgKeeper(ArgRootType):
    \"""
        `ArgKeeper` is used to set and maintain value for an arg in `ArgManager`. It shares similarity with `ArgSetter` that both of them are used to set value for an arg, but they are different in that `ArgKeeper` is used to set and maintain value for an arg in the long run, while `ArgSetter` is used to set value for an arg only once.
        
        `ArgKeeper` should only be used to instantiate `ArgManager`.
    \"""
    _all_supported_keepers = {
        'fixed': lambda state, **kwargs: state.previous_value,
    }
    # SUBCLASS

    def _get_keeper_func(self, keeper: OptionalFunc) -> Callable:
        return self._get_func_recursive(keeper or 'none', self._all_supported_keepers, "keeper")

    def __init__(
        self,
        keeper: RobustOptionalFuncArgsTuple = None,
    ):
        super().__init__()
        keeper, self.keeper_args = self._parse_func_arg_tuple(keeper)
        self.keeper = self._get_keeper_func(keeper)
        self._logger.debug(f"{repr(self)} initiated with keeper {repr(keeper)}.")

    def __call__(self, state: AttrDict) -> Any:
        result = self.keeper(state, *self.keeper_args)
        self._logger.debug(f"{repr(self)} called, result: {repr(result)}.")
        return result


class _ArgKeeper(ArgKeeper):
    _all_supported_keepers = {
        'fixed': lambda state, **kwargs: state.previous_value,
    }
"""


# ------------------------------------ Module Postprocess ------------------------------------ #

def _module_postprocess():
    
    def _repr_function(name, func):
        if func.__name__ == '<lambda>':
            func.__name__ = '_'+name
            func.__qualname__ = func.__qualname__.split('<lambda>', 1)[0] + func.__name__
        return f'{func.__qualname__}({repr(get_func_param(func))})'
        
    module_report = {}
    global_vars = globals().copy()
    for var_name, var_value in global_vars.items():
        if var_name in __all__:
            if issubclass(var_value, ArgSetter):
                module_report[repr(var_value.__qualname__)] = {name: _repr_function(name, func) for name, func in var_value._all_supported_setters.items()}
            # elif issubclass(var_value, ArgKeeper):
            #     module_report[repr(var_value.__qualname__)] = {name: _repr_function(name, func) for name, func in var_value._all_supported_keepers.items()}
    module_ref_path = 'docs/refs'
    if not os.path.exists(module_ref_path):
        os.makedirs(module_ref_path)
    logger.debug(f"module {__name__} loaded:\n{json.dumps(module_report, indent=4, ensure_ascii=False)}\n")
    with open(os.path.join(module_ref_path, f'{__name__}.json'), 'w') as f:
        json.dump(module_report, f, indent=4, ensure_ascii=False)

_module_postprocess()
logger.info(f"module {__name__} imported")