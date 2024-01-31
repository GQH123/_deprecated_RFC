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
    # _item_queue: ListProxy[ref[Item]] = RFC_GLOBAL_MANAGER.list()
    
    # _item_type_register = None  # Dict[str, ItemType], register of all `ItemType`s, DO NOT SUBCLASS
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
        # RootQueue._item_type_register = manager.dict()
        RootQueue._step = manager.Value('i', 0)
    
    @classmethod
    def _add(cls, item) -> None:
        """
            Add a new item to `RootQueue`.
        """
        # cls._logger.debug(cls._root_item_queue)
        lock = get_global_lock()
        with lock:
            RootQueue._step.value += 1
            RootQueue._root_item_queue.append(item_tuple)  # type: ignore # now the item is of type `Item` but not `ItemType`
            if RootQueue._step.value & 1023 == 0:
                RootQueue._logger.info(f"{RootQueue._step.value} items added")
                RootQueue._logger.info(f"{repr(item)} added")
                cls._logger.info(f"{RootQueue._step.value} items added")
                cls._logger.info(f"{repr(item)} added")
        # cls._logger.info(f"{repr(item_tuple)} added to {repr(cls)}")
        # RootQueue._logger.info(f"{repr(item_tuple)} added to {repr(cls)}")
        # cls._item_queue.append(weakref.ref(item, cls._remove_item_weakref))
        
    @classmethod
    def fetch(cls):  # cls must be RootQueue in this case
        # cls._logger.debug(cls._root_item_queue)
        lock = get_global_lock()
        with lock:
            if not RootQueue._root_item_queue:
                # cls._logger.debug(f"None fetched from {repr(cls)}")
                return None
            # item_tuple = cls._root_item_queue.pop()
            item = RootQueue._root_item_queue.pop()
        # cls_name, id, extra_args, extra_kwargs = item_tuple
        # with lock:
        #     item = cls._item_type_register[cls_name](id, *extra_args, **extra_kwargs)
        item.pend()
        RootQueue._logger.info(f"{repr(item)} fetched")  
        return item
    
    """
    @classmethod
    def _remove_item_weakref(cls, _ref):
        if _ref in cls._item_queue:
            cls._item_queue.remove(_ref)
    """


RootQueue._get_logger(__name__, level='info')


# ------------------------------------ Module Postprocess ------------------------------------ #

logger.info(f"module {__name__} imported")