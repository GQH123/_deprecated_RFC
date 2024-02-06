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
    _active_item_count = None  # : ValueProxy, number of active items
    _active_adder_count = None
    _step = None

    def __init__(self):
        """
            `RootQueue` should never be instantiated.
        """
        raise ValueError(f"{repr(self)} should never be called")
    
    @classmethod
    def lazy_init(cls):  # lazy init for pickle error, must be called after any custom `ItemType` definition
        manager = get_global_manager()
        RootQueue._root_item_queue = manager.list()
        RootQueue._step = manager.Value('i', 0)
        RootQueue._active_item_count = manager.Value('i', 0)
        RootQueue._active_adder_count = manager.Value('i', 0)
    
    @classmethod
    def add(cls, item) -> None:
        """
            Add a new item to `RootQueue`.
        """
        with get_global_lock():
            RootQueue._step.value += 1
            RootQueue._root_item_queue.append(item)  # type: ignore # now the item is of type `Item` but not `ItemType`
            if RootQueue._step.value & 1023 == 0:
                RootQueue._logger.info(f"{RootQueue._step.value} items added, active items count = {RootQueue._active_item_count.value}, active adders count = {RootQueue._active_adder_count.value}")
                RootQueue._logger.info(f"{repr(item)} added")
                cls._logger.info(f"{RootQueue._step.value} items added")
                cls._logger.info(f"{repr(item)} added")
        
    @classmethod
    def fetch(cls):  # cls must be RootQueue in this case
        with get_global_lock():
            if not RootQueue._root_item_queue:
                assert RootQueue._active_item_count.value >= 0 and RootQueue._active_adder_count.value >= 0, f"error occurs in RootQueue, remain_active_items={RootQueue._active_item_count.value}, remain_active_adders={RootQueue._active_adder_count.value}"
                if RootQueue._active_item_count.value == 0 and RootQueue._active_adder_count.value == 0:
                    return 'QUIT'
                else:
                    return 'WAIT'
            item = RootQueue._root_item_queue.pop()
            RootQueue._active_item_count.value += 1  # this will be reduced in item.finish()
        item.pend()
        # RootQueue._logger.info(f"{repr(item)} fetched")  
        return item


RootQueue._get_logger(__name__, level='info')


# ------------------------------------ Module Postprocess ------------------------------------ #

logger.info(f"module {__name__} imported")