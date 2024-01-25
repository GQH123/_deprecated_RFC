from typing import Any

from ..utils.cls import RootType
from ..utils.ds import AttrDict
from ..item.item import Item

__all__ = [
]


class MiddleWare(RootType):
    def __init__(
        self,
        middleware_args: AttrDict
    ):
        super().__init__()
        self._get_logger()
        self._args = middleware_args
        self._logger.info(f"{repr(self)} initialized")
    
    def _apply(
        self,
        item: Item,
        result: Any,
    ):
        return result
    # SUBCLASS
    
    def _handle_error(
        self,
        error: Exception,
        item: Item,
        result: Any,
    ):
        raise error
    # SUBCLASS
        
    def apply(
        self,
        item: Item,
        result: Any,
    ):
        try:
            _result = self._apply(item, result)
            self._logger.info(f"{repr(self)} applied on {repr(item)}")
            return _result
        except Exception as e:
            self._logger.info(f"{repr(self)} failed on {repr(item)}, caught error {repr(e)}")
            self._handle_error(e, item, result)


class _MiddleWare(MiddleWare):
    def _apply(
        self,
        item: Item,
        result: Any,
    ):
        ...
    
    def _handle_error(
        self,
        error: Exception,
        item: Item,
        result: Any,
    ):
        ...