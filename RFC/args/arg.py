import os
import json
import string
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
    'IsLeafSetter',
    'RetryLimitSetter',
    'TimeoutSetter',
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


class ArgSetter(ArgRootType):
    """
        `ArgSetter` is used to set value for an arg in `ArgGroup`. It is designed to be convenient for setting args for multiple `Item`s in one `Itemset`, so it in fact represents NOT the value, but the generating method of it. Actual value of args are attached to `Item`s.
        
        `ArgSetter` should only be used to instantiate `ArgGroup`.
    """
    _name: str = 'argsetter'

    @staticmethod
    def _not_set(id, arg_group, **kwargs):
        raise ValueError(f"arg {repr(kwargs['self'])} not set in {repr(arg_group)}")
    
    @staticmethod
    def _field(id, arg_group, template, **kwargs):
        kwargs['id'] = id
        return template.format(**{field: kwargs.get(field, None) for field in [parse_tuple[1] for parse_tuple in list(string.Formatter().parse(template))]})
        
    _all_supported_setters = {
        'fixed': lambda id, arg_group, value, **kwargs: value,
        'none': lambda id, arg_group, **kwargs: None,
        'not_set': _not_set,
        'field': _field,
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
        ArgSetter._get_logger(__name__, level='info', propagate=False)
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
    @staticmethod
    def _set_api_info(id, arg_group, api_type, api_key, api_passwd, **kwargs):
        return {
            'api_type': api_type,
            'api_key': api_key,
            'api_passwd': api_passwd,
        }

    _all_supported_setters = {
        'api': _set_api_info,
    }


class StreamSetter(ArgSetter):
    pass


class IsLeafSetter(ArgSetter):
    pass


class RetryLimitSetter(ArgSetter):
    pass


class TimeoutSetter(ArgSetter):
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
                # 'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7,en-GB;q=0.6,ru;q=0.5',
            },
            'none': {},
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
        prefix = ArgSetter._field(id, arg_group, prefix, **kwargs)
        sep = ArgSetter._field(id, arg_group, sep, **kwargs)
        save_dir = prefix
        for item_type_name, item_id in arg_group.bloodline[:-1]:
            save_dir = os.path.join(save_dir, str(item_id), sep)
        save_dir = os.path.join(save_dir, str(arg_group.bloodline[-1][1]))
        return save_dir

    _all_supported_setters = {
        'auto': _auto,
    }


class BloodlineSetter(ArgSetter):
    @staticmethod
    def _inherit(id, arg_group, _bld=None, **kwargs):
        _bld = kwargs.get('bloodline', None)
        if _bld is None:
            _bld = []
        return _bld + [(kwargs['_item_type'], id)]

    _all_supported_setters = {
        'inherit': _inherit,
    }


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
    module_ref_path = 'docs/refs'
    if not os.path.exists(module_ref_path):
        os.makedirs(module_ref_path)
    logger.debug(f"module {__name__} loaded:\n{json.dumps(module_report, indent=4, ensure_ascii=False)}\n")
    with open(os.path.join(module_ref_path, f'{__name__}.json'), 'w') as f:
        json.dump(module_report, f, indent=4, ensure_ascii=False)

_module_postprocess()
logger.info(f"module {__name__} imported")