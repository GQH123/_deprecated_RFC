import os
import json
from typing import Callable, Dict, Any

from ..utils.log import get_logger
from ..utils.cls import RootType
from ..utils.ds import AttrDict
# from ..item.item import Item  # for circular import issue we cannot import `Item` for typing

logger = get_logger(__name__)
logger.info(f"importing module {__name__}")

try:
    import requests
except Exception as e:
    error_report = f'[{repr(type(e).__name__)}] {repr(e)}'
    logger.warning(f"failed to import requests, caught error {error_report}")
    requests = None

try:
    import aiohttp
except Exception as e:
    error_report = f'[{repr(type(e).__name__)}] {repr(e)}'
    logger.warning(f"failed to import aiohttp, caught error {error_report}")
    aiohttp = None

try:
    import asks
except Exception as e:
    error_report = f'[{repr(type(e).__name__)}] {repr(e)}'
    logger.warning(f"failed to import asks, caught error {error_report}")
    asks = None


__all__ = [
    'RequestsSession',
    'AioHTTPSession',
    'AsksSession',
]


class SessionMeta(type):
    keyword = ['_defined_args']

    def __new__(cls, clsname, bases, attrs):
        for name, val in attrs.items():
            if not isinstance(val, dict) or name not in cls.keyword:
                continue
            inherited_dict = {}
            for base in bases:
                if hasattr(base, name):
                    inherited_dict.update(getattr(base, name))
            inherited_dict.update(val)
            attrs[name] = inherited_dict
        return super().__new__(cls, clsname, bases, attrs)


class Session(AttrDict, RootType, metaclass=SessionMeta):
    """
        `Session` is responsible for requesting items, each subclass on behalf a different request lib, except for `Session` itself.
    """
    _name: str = 'session'  # SUBCLASS
    
    _request_lib: str = 'not_set'   # SUBCLASS, set this to the name of the request lib
    _async_lib: str = 'not_set'     # SUBCLASS, set this to the name of the async lib, 'none' if not async
    _defined_args = {
        'lib': 'not_set',
        'no_session': False,
    }  # SUBCLASS, expected init args with default value for this session

    def __init__(
        self,
        session_args: AttrDict
    ):
        self._get_logger_self(__name__)
        _args = AttrDict()
        for arg in session_args:
            if arg not in self._defined_args:
                self._logger.warning(f"arg {repr(arg)} not defined")
                continue
            _args[arg] = session_args[arg]
        for defined_arg in self._defined_args:
            if defined_arg not in _args:
                _args[defined_arg] = self._defined_args[defined_arg]
                self._logger.info(f"arg {repr(defined_arg)} not set, using default {repr(self._defined_args[defined_arg])}")
        super().__init__(_args)
        self._logger.info("initialized")
        self._session = self._get_session()
        self._logger.info(f"session created, {repr(self)}")

    def _get_session(
        self,
    ):
        """
            Here you should implement session/no_session getting for correspoding request lib.
        """
        ...
    # SUBCLASS
    
    def request(
        self,
        item,
    ) -> Any:
        """
            Here you should implement session requesting for correspoding request lib.
            
            Note that if `self._async_lib` is not 'none', then this method should be async.
        """
        ...
    # SUBCLASS
    
    def close(
        self,
    ):
        """
            Here you should implement session closing for correpoding request lib.
            
            Note that if `self._async_lib` is not 'none', then this method should be async.
        """
        ...
    # SUBCLASS
    
    def __repr__(self):
        cls_repr = f'{repr(self.__class__.__qualname__)}'
        args_repr = repr({args: self[args] for args in self._defined_args})
        return f'{cls_repr}({args_repr})'


class _Session(Session):
    _name: str = ...
    
    _request_lib: str = 'not_set'
    _async_lib: str = 'not_set'
    _defined_args = {
    }

    def _get_session(
        self,
    ):
        ...
    
    def request(
        self,
        item,
    ) -> Any:
        ...
    
    def close(
        self,
    ):
        ...


class RequestsSession(Session):
    _name: str = 'session_requests'

    _request_lib: str = 'requests'
    _async_lib: str = 'none'
    _defined_args = {
        'cookies': {},
        'proxies': None,  # example: {'http': 'foo.bar:3128', 'http://host.name': 'foo.bar:4012'}
        'headers': {},
    }

    def _get_session(
        self,
    ):
        if self.no_session:
            s = AttrDict()
            s.request = requests.request  # request method is the key method of requests.Session
        else:
            if requests is None:
                raise ValueError(f"request_lib {repr(self._request_lib)} is not supported in this environment")
            s = requests.Session()
            if self.cookies:
                s.cookies = requests.cookies.cookiejar_from_dict(self.cookies)
            if isinstance(self.proxies, dict):
                s.proxies = self.proxies
            else:
                raise ValueError(f"proxies type should be {repr(dict)}, not {repr(type(self.proxies))}")
            s.headers.update(self.headers)
        return s
        
    def request(
        self,
        item,
    ) -> Any:
        """
        return self._session.request(
            method=item.method,
            url=item.url,
            params=item.params,
            data=item.data,
            json=item.json,
            headers=item.headers,
            cookies=item.cookies,
            files=item.files,
            auth=item.auth,
            timeout=item.timeout,
            allow_redirects=item.allow_redirects,
            proxies=item.proxies,
            hooks=item.hooks,
            stream=item.stream,
            verify=item.verify,
            cert=item.cert,
            jsonable_encoder=item.jsonable_encoder,
            **item.kwargs,
        )
        """
        return self._session.request(
            method = item.method,
            url=item.url,
            params=item.params,
            data=item.payload,
            headers=item.headers.update({
                'user-agent': item.user_agent,
                'referer': item.referer,
            }),
            allow_redirects=True,
            cookies=item.cookies,
            proxies=item.proxies,
            stream=item.stream,  # is you want to use StreamDownloadersession, this must be True
        )  # only support these args for now
    
    def close(
        self,
    ):
        self._session.close()


class AioHTTPSession(Session):
    _name: str = 'session_aiohttp'

    _request_lib: str = 'aiohttp'
    _async_lib: str = 'asyncio'
    _defined_args = {
    }

    def _get_session(
        self,
    ):
        ...
    
    async def request(
        self,
        item,
    ) -> Any:
        ...
    
    async def close(
        self,
    ):
        ...
    
    
class AsksSession(Session):
    _name: str = 'session_asks'

    _request_lib: str = 'asks'
    _async_lib: str = 'trio'
    _defined_args = {
    }

    def _get_session(
        self,
    ):
        ...
    
    async def request(
        self,
        item,
    ) -> Any:
        ...
    
    async def close(
        self,
    ):
        ...
    

# ------------------------------------ Module Postprocess ------------------------------------ #

_nameToSession = {
    'requests': RequestsSession,
    'aiohttp': AioHTTPSession,
    'asks': AsksSession
}

__all__ = [cls.__name__ for cls in list(_nameToSession.values())] + ['get_session']


def get_session(session_args: AttrDict, logger=None):
    try:
        session_name = session_args.lib
        session = _nameToSession[session_name](session_args)
        return session
    except Exception as e:
        if logger is not None:
            error_report = f'[{repr(type(e).__name__)}] {repr(e)}'
            logger.error(f"failed to initialize session {repr(session_name)} with args {repr(session_args[session_name])}, caught error {error_report}")
        raise e


def _module_postprocess():
    module_report = {}
    for var_name, var_value in globals().items():
        if var_name in __all__ and isinstance(var_value, type):
            module_report[repr(var_value.__qualname__)] = {name: repr(setter) for name, setter in var_value._defined_args.items()}
    logger.debug(f"module {__name__} loaded:\n{json.dumps(module_report, indent=4, ensure_ascii=False)}\n")
    module_ref_path = 'docs/refs'
    if not os.path.exists(module_ref_path):
        os.makedirs(module_ref_path)
    with open(os.path.join(module_ref_path, f'{__name__}.json'), 'w') as f:
        json.dump(module_report, f, indent=4, ensure_ascii=False)


_module_postprocess()
logger.info(f"module {__name__} imported")