from typing import List, Callable, Dict, Iterable, Any

from RFC.core.utils.cls import RootType
from RFC.core.utils.ds import AttrDict
from RFC.core.item.item import Item


class Session(RootType):
    """
        `Session` is responsible for requesting items, each subclass on behalf a different request lib, except for `Session` itself.
    """
    _request_lib: str = 'not_set'   # SUBCLASS
    _async_lib: str = 'not_set'     # SUBCLASS
    _all_supported_methods: Dict[str, Callable] = {
        'get': lambda session, item: None,
        'post': lambda session, item: None,
    } # SUBCLASS, you should implement functions for each of these different requesting methods
    
    def __init__(
        self,
        session_args: AttrDict,
    ):
        super().__init__()
        self._get_logger()
        self._session_args = session_args
        self._session = None
        self._no_session = None
        
    def _get_session(
        self,
        item: Item,
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
        method_func = self._get_func_recursive(item.method, self._all_supported_methods)
        session = self._get_session(item)
        return method_func(session, item)
    
    def close(
        self,
    ):
        """
            Here you should implement session closing for correpoding request lib.
        """
        ...
    # SUBCLASS
    
    
class _Session(Session):
    _request_lib: str = 'not_set'
    _async_lib: str = 'not_set'
    _all_supported_methods: Dict[str, Callable] = {
        'get': lambda session, item: None,
        'post': lambda session, item: None,
    }
        
    def _get_session(
        self,
        item: Item,
    ):
        ...
    
    def close(
        self,
    ):
        ...


class RequestsSession(Session):
    _request_lib: str = 'requests'
    _async_lib: str = 'none'
    _all_supported_methods: Dict[str, Callable] = {
        'get': lambda session, item: None,
        'post': lambda session, item: None,
    }
        
    def _get_session(
        self,
        item: Item,
    ):
        ...
    
    def close(
        self,
    ):
        ...