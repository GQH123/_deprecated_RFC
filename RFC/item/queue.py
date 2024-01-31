from typing import Any
# from multiprocessing.managers import ListProxy

from ..utils.cls import RootType
from ..utils.ds import AttrDict
from ..utils.defs import (
    get_global_lock,
    get_global_manager,
)
from ..utils.log import get_logger

logger = get_logger(__name__)
logger.info(f"importing module {__name__}")


class RootQueue(RootType):
    _name: str = 'rootqueue'
    
    _root_item_queue = None  # : ListProxy[Item], queue of items to be processed
    _step = None

    def __init__(self):
        """
            `RootQueue` should never be instantiated.
        """
        raise ValueError(f"{repr(self)} should never be called")
    
    @classmethod
    def _lazy_init(cls):  # lazy init for pickle error, must be called after any custom `ItemType` definition
        manager = get_global_manager()
        RootQueue._root_item_queue = manager.list()
        RootQueue._step = manager.Value('i', 0)
    
    @classmethod
    def _add(cls, item) -> None:
        """
            Add a new item to `RootQueue`.
        """
        lock = get_global_lock()
        with lock:
            RootQueue._step.value += 1
            RootQueue._root_item_queue.append(item_tuple)  # type: ignore # now the item is of type `Item` but not `ItemType`
            if RootQueue._step.value & 1023 == 0:
                RootQueue._logger.info(f"{RootQueue._step.value} items added")
                RootQueue._logger.info(f"{repr(item)} added")
                cls._logger.info(f"{RootQueue._step.value} items added")
                cls._logger.info(f"{repr(item)} added")
        
    @classmethod
    def fetch(cls):  # cls must be RootQueue in this case
        lock = get_global_lock()
        with lock:
            if not RootQueue._root_item_queue:
                return None
            item = RootQueue._root_item_queue.pop()
        item.pend()
        RootQueue._logger.info(f"{repr(item)} fetched")  
        return item


RootQueue._get_logger(__name__, level='info')


# ------------------------------------ Module Postprocess ------------------------------------ #

logger.info(f"module {__name__} imported")