import time
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
    
    _initialized: bool = False
    
    _root_item_queue = None  # : ListProxy[Item], queue of items to be processed
    _active_item_count = None  # : ValueProxy, number of active items
    _active_adder_count = None
    _step = None
    
    _report_wait_time = 10  # seconds

    def __init__(self):
        """
            `RootQueue` should never be instantiated.
        """
        raise ValueError(f"{repr(self)} should never be called")
    
    @classmethod
    def lazy_init(cls):  # lazy init for pickle error, must be called after any custom `ItemType` definition
        manager = get_global_manager()
        RootQueue._root_item_queue = manager.list()
        RootQueue._prior_item_queue = manager.list()
        RootQueue._step = manager.Value('i', 0)
        RootQueue._active_item_count = manager.Value('i', 0)
        RootQueue._active_adder_count = manager.Value('i', 0)
        RootQueue._initialized = True
    
    @classmethod
    def add(cls, item) -> None:
        """
            Add a new item to `RootQueue`.
        """
        _added_queue = RootQueue._root_item_queue if not item._prior_queue else RootQueue._prior_item_queue
        # in case queue is too long, wait for a while ~(or the last item block the queue, [deprecated, too slow])
        while True:
            wait_for_queue = False
            with get_global_lock():
                queue_len = len(_added_queue)
            wait_for_queue = (queue_len >= 100000)
            if wait_for_queue:
                time.sleep(10)
            else:
                break
        with get_global_lock():
            RootQueue._step.value += 1
            _added_queue.append(item)  # type: ignore # now the item is of type `Item` but not `ItemType`
            if RootQueue._step.value & 1023 == 0:
                RootQueue._logger.info(f"{repr(item)} added")
                # cls._logger.info(f"{RootQueue._step.value} items added")
                # cls._logger.info(f"{repr(item)} added")
    
    @classmethod
    def report(cls):
        while True:
            with get_global_lock():
                if not RootQueue._root_item_queue and not RootQueue._prior_item_queue and RootQueue._active_item_count.value == 0 and RootQueue._active_adder_count.value == 0:
                    RootQueue._logger.info(f"all items finished, RootQueue will be closed")
                    return
                RootQueue._logger.info(f"{RootQueue._step.value} items added, qic = {len(RootQueue._root_item_queue)}, prqic = {len(RootQueue._prior_item_queue)}, aic = {RootQueue._active_item_count.value}, aac = {RootQueue._active_adder_count.value}")
            time.sleep(RootQueue._report_wait_time)

    @classmethod
    def fetch(cls):  # cls must be RootQueue in this case
        with get_global_lock():
            _fetched_queue = RootQueue._prior_item_queue if RootQueue._prior_item_queue else RootQueue._root_item_queue
            if not _fetched_queue:  # it is impossible that prior queue is empty now
                # assert RootQueue._active_item_count.value >= 0 and RootQueue._active_adder_count.value >= 0, f"error occurs in RootQueue, remain_active_items={RootQueue._active_item_count.value}, remain_active_adders={RootQueue._active_adder_count.value}"
                if RootQueue._active_item_count.value == 0 and RootQueue._active_adder_count.value == 0:
                    return 'QUIT'
                else:
                    return 'WAIT'
            item = _fetched_queue.pop()
            RootQueue._active_item_count.value += 1  # this will be reduced in item.finish()
        item.pend()
        # RootQueue._logger.info(f"{repr(item)} fetched")  
        return item


RootQueue._get_logger(__name__, level='info')


# ------------------------------------ Module Postprocess ------------------------------------ #

logger.info(f"module {__name__} imported")