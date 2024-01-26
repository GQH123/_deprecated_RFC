from typing import Callable, Dict, Any

from ..utils.cls import RootType
from ..utils.ds import AttrDict
from ..item.item import Item

__all__ = [
    'RequestsSession',
    'AioHTTPSession',
    'AsksSession',
]


class Session(RootType):
    """
        `Session` is responsible for requesting items, each subclass on behalf a different request lib, except for `Session` itself.
    """
    _request_lib: str = 'not_set'   # SUBCLASS, set this to the name of the request lib
    _async_lib: str = 'not_set'     # SUBCLASS, set this to the name of the async lib, 'none' if not async

    def __init__(
        self,
        session_args: AttrDict,
    ):
        super().__init__()
        self._get_logger()
        self._session = self._get_session(session_args)

    def _get_session(
        self,
        session_args: AttrDict
    ):
        """
            Here you should implement session/no_session getting for correspoding request lib.
        """
        ...
    # SUBCLASS
    
    def request(
        self,
        item: Item
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


class _Session(Session):
    _request_lib: str = 'not_set'
    _async_lib: str = 'not_set'

    def _get_session(
        self,
        session_args: AttrDict
    ):
        ...
    
    def request(
        self,
        item: Item
    ) -> Any:
        ...
    
    def close(
        self,
    ):
        ...


class RequestsSession(Session):
    _request_lib: str = 'requests'
    _async_lib: str = 'none'

    def _get_session(
        self,
        session_args: AttrDict
    ):
        ...
    
    def request(
        self,
        item: Item
    ) -> Any:
        ...
    
    def close(
        self,
    ):
        ...


class AioHTTPSession(Session):
    _request_lib: str = 'aiohttp'
    _async_lib: str = 'asyncio'

    def _get_session(
        self,
        session_args: AttrDict
    ):
        ...
    
    async def request(
        self,
        item: Item
    ) -> Any:
        ...
    
    async def close(
        self,
    ):
        ...
    
    
class AsksSession(Session):
    _request_lib: str = 'asks'
    _async_lib: str = 'trio'

    def _get_session(
        self,
        session_args: AttrDict
    ):
        ...
    
    async def request(
        self,
        item: Item
    ) -> Any:
        ...
    
    async def close(
        self,
    ):
        ...