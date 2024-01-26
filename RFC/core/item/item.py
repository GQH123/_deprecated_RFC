# import weakref
# from weakref import ref
from time import time
from multiprocessing.managers import ListProxy
from typing import Any, Callable, Dict, Mapping

from ..utils.ds import AttrDict
from ..utils.cls import RootType
from ..utils.defs import (
    PENDING,
    PROCESSING,
    FAILED,
    FINISHED,
    GENERATING,
    _itemStatusToName,
    RFC_GLOBAL_MANAGER,
    RFC_GLOBAL_LOCK,
)
from ..args.arg_group import ArgGroup

__all__ = [
    'ItemType'
]


class Item(AttrDict, RootType):
    """
        `Item` is the instance of `ItemType`, which is the unit of crawling. `Item` is fixed across different `ItemType`s, you should never subclass it.
        
        Note that `item`s may be arranged to and crawled in different threads/processings. Any raised errors will not be able to interrupt the main process, they will be handled and recorded in each `item` separately.
    """
    def __init__(
        self,
        args: AttrDict,
        generate: Callable[[Any], None],
    ):
        if 'id' not in args:
            raise ValueError(f"no id in {repr(args)}, which is required for items")
        if 'bloodline' not in args:
            raise ValueError(f"no bloodline in {repr(args)}, which is required for items")
        super().__init__(args)
        self._get_logger(repr(self.id))  # type: ignore
        self._status = None     
        self._timestamp = {}                        # Dict[str, int | str], timestamp of each status
        self._generate = generate
        
    def __repr__(self):
        return f"{self.bloodline[-1].__name__}({repr(self.id)})"  # type: ignore

    def _status_check(self, status: int):
        if status not in _itemStatusToName:
            raise ValueError(f"unknown updated status {repr(status)} in {repr(self)}")
        if self._status not in _itemStatusToName:
            raise ValueError(f"unknown self status {repr(self._status)} in {repr(self)}")
        if self._status is None:
            if not status == PENDING:
                raise ValueError(f"cannot update status from {repr(_itemStatusToName[self._status])} to {repr(_itemStatusToName[status])} in {repr(self)}, it should be {repr(_itemStatusToName[PENDING])}")
        elif self._status == PENDING:
            if not status == PROCESSING:
                raise ValueError(f"cannot update status from {repr(_itemStatusToName[self._status])} to {repr(_itemStatusToName[status])} in {repr(self)}, it should be {repr(_itemStatusToName[PROCESSING])}")
        elif self._status == PROCESSING:
            if not status in [FAILED, GENERATING]:
                raise ValueError(f"cannot update status from {repr(_itemStatusToName[self._status])} to {repr(_itemStatusToName[status])} in {repr(self)}, it should be {repr(_itemStatusToName[FAILED])} or {repr(_itemStatusToName[FINISHED])}")
        elif self._status == GENERATING:
            if not status in [FAILED, FINISHED]:
                raise ValueError(f"cannot update status from {repr(_itemStatusToName[self._status])} to {repr(_itemStatusToName[status])} in {repr(self)}, it should be {repr(_itemStatusToName[FAILED])} or {repr(_itemStatusToName[FINISHED])}")
        elif self._status in [FAILED, FINISHED]:
            raise ValueError(f"cannot update status from {repr(_itemStatusToName[self._status])} to {repr(_itemStatusToName[status])} in {repr(self)}, no more status is allowed")

    def _update_status(self, status: int, check_status: bool=False):
        if check_status:
            self._status_check(status)
        self._timestamp[status] = time()
        self._logger.info(f"status updated from {repr(_itemStatusToName[self._status] if self._status is not None else None)} to {repr(_itemStatusToName[status])}")  
        self._status = status
        
    def pend(self):
        self._update_status(PENDING)
        
    def process(self):
        self._update_status(PROCESSING)
        
    def finish(self, if_ok: bool, result: Any=None):
        if not if_ok:
            self._update_status(FAILED)
            return
        self._update_status(GENERATING)
        try:
            self._generate(result)
        except Exception as e:
            self._update_status(FAILED)
            raise e
        else:
            self._update_status(FINISHED)


class ItemType(RootType):
    _defined_arg_groups: Dict[str, ArgGroup] = { # define arg_groups in this ItemType, str as group name, ArgGroup as default for this group
    } # SUBCLASS
    
    _root_item_queue: ListProxy[Item] = RFC_GLOBAL_MANAGER.list()  # queue of items to be processed
    
    # _item_queue: ListProxy[ref[Item]] = RFC_GLOBAL_MANAGER.list() # SUBCLASS, queue of weakref to items in this ItemType, should be subclassed  # deprecated, cannot maintain weakref across multi-processings

    def __init__(self):
        """
            `ItemType` serves as the unit of requesting, which is normally responsible for a repetitious kind of a crawler target, such as pages of a website, or a specific kind of API.
            
            When trying to crawl a whole website, there can be many such intermediate targets organized in a tree-like structure, and `ItemType` can be regarded as the representation of each node in the tree.
            
            `ItemType` should not be instantiated, you should subclass it and define `ArgGroup`s in class definition.
        """
        raise ValueError(f"{repr(self)} should never be called")
    
    def __new__(cls, id, *extra_args, **extra_kwargs):
        """
            Call `ArgGroup`s in this `ItemType`.
        """
        args_value = {}
        for arg_group in cls._defined_arg_groups:
            args_value.update(cls._defined_arg_groups[arg_group](id, *extra_args, **extra_kwargs))
        if 'id' not in args_value:
            args_value['id'] = id
        return Item(AttrDict(args_value), cls._generate)
    
    """
    @classmethod
    def _remove_item_weakref(cls, _ref):
        if _ref in cls._item_queue:
            cls._item_queue.remove(_ref)
    """
    
    @classmethod
    def _add_item(cls, id: Any, *extra_args, **extra_kwargs) -> None:
        """
            Add a new item to the queue of this `ItemType`.
        """
        item = cls(id, *extra_args, **extra_kwargs)
        item.pend()  # type: ignore # now the item is of type `Item` but not `ItemType`
        with RFC_GLOBAL_LOCK:
            cls._root_item_queue.append(item)  # type: ignore # now the item is of type `Item` but not `ItemType`
        # cls._item_queue.append(weakref.ref(item, cls._remove_item_weakref))
        
    @classmethod
    def fetch(cls):
        with RFC_GLOBAL_LOCK:
            if not cls._root_item_queue:
                return None
            return cls._root_item_queue.pop()

    @classmethod
    def _generate(cls, result: Any) -> None:
        """
            You need to parse the result first, then generate new items of some `ItemType`s.

            New items should be added directly through class method `_add_item` of other `ItemType`s. This function should not return anything.
            
            Note that you should add new items in reversee order. Because `item`s will be fetched from the end of the queue, so that the newly added `item`s will be processed first.
        """
        pass
    # SUBCLASS

    @classmethod
    def __repr__(cls):
        return f"{cls.__name__}({repr(cls._defined_arg_groups)})"


class _ItemType(ItemType):
    # _item_queue: ListProxy[ref[Item]] = RFC_GLOBAL_MANAGER.list()
    _defined_arg_groups: Dict[str, ArgGroup] = {
    }
    @classmethod
    def _generate(cls, result: Any) -> None:
        ...