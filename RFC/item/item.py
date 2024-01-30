# import weakref
# from weakref import ref
from time import time
from typing import Any, Callable, Dict

from ..utils.ds import AttrDict
from ..utils.cls import RootType
from ..utils.defs import (
    PENDING,
    PROCESSING,
    FAILED,
    FINISHED,
    GENERATING,
    _itemStatusToName,
    get_global_lock,
)
from ..args.arg_group import (
    # ArgGroup,
    RequestArgGroup,
    ItemArgGroup,
)
from ..utils.log import get_logger

logger = get_logger(__name__)
logger.info(f"importing module {__name__}")

from .queue import RootQueue
from .entry import Entry

__all__ = [
    'ItemType'
]


class Item(AttrDict, RootType):
    """
        `Item` is the instance of `ItemType`, which is the unit of crawling. `Item` is fixed across different `ItemType`s, you should never subclass it.
        
        Note that `item`s may be arranged to and crawled in different threads/processings. Any raised errors will not be able to interrupt the main process, they will be handled and recorded in each `item` separately.
    """
    _name: str = 'item'
    
    def __init__(
        self,
        args: AttrDict,
        generate: Callable[[Any], None],
    ):
        if 'id' not in args:
            raise ValueError(f"no id in {repr(args)}, which is required for items")
        if 'bloodline' not in args:
            raise ValueError(f"no bloodline in {repr(args)}, which is required for items")
        if 'save_dir' not in args:
            raise ValueError(f"no save_dir in {repr(args)}, which is required for items")
        super().__init__(args)
        self._get_logger_self(name=f"{self.bloodline[-1][0]}({repr(self.bloodline[-1][1])})", log_path=self.save_dir, level='info')  # type: ignore
        self._status = None     
        self._timestamp = {}                        # Dict[str, int | str], timestamp of each status
        self._generate = generate
        
    def __repr__(self):
        return '.'.join([f"{bloodline_item[0]}({str(bloodline_item[1])})" for bloodline_item in self.bloodline])

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
            self._generate(item=self, result=result)
        except Exception as e:
            self._update_status(FAILED)
            raise e
        else:
            self._update_status(FINISHED)


class ItemTypeMeta(type):
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
        new_cls = super().__new__(cls, clsname, bases, attrs)
        new_cls._get_logger(__name__, level='info')
        return new_cls


class ItemType(RootQueue, Entry, metaclass=ItemTypeMeta):
    """
        `ItemType` serves as the unit of requesting, which is normally responsible for a repetitious kind of a crawler target, such as pages of a website, or a specific kind of API.
        
        When trying to crawl a whole website, there can be many such intermediate targets organized in a tree-like structure, and `ItemType` can be regarded as the representation of each node in the tree.
        
        `ItemType` should not be instantiated, you should subclass it and define `ArgGroup`s in class definition.
    """
    _name: str = 'itemtype'  # SUBCLASS
    
    # _defined_arg_groups: Dict[str, ArgGroup] = {    # define arg_groups in this ItemType, str as group name, ArgGroup as default for this group
    # } # SUBCLASS
    
    request_arg_group: dict = {}  # : RequestArgGroup = RequestArgGroup()  # SUBCLASS
    item_arg_group: dict = {}  # : ItemArgGroup = ItemArgGroup()           # SUBCLASS
    
    requestor_args: dict = {}  # : RequestorArgs = RequestorArgs()         # SUBCLASS
    middleware_args: dict = {}  # : dict[str, MiddlewareArgs] = {}         # SUBCLASS
    session_args: dict = {}  # : SessionArgs = SessionArgs(lib='not_set')  # SUBCLASS

    # _session = None       # OPTIONAL[SUBCLASS]
    # _middleware = None    # OPTIONAL[SUBCLASS]
    # _requestor = None     # OPTIONAL[SUBCLASS]
    _logger = None          # OPTIONAL[SUBCLASS]

    def __new__(cls, id, *extra_args, **extra_kwargs):
        """
            Call `ArgGroup`s in this `ItemType`.
        """
        args_value = {}
        # for arg_group in cls._defined_arg_groups:
        #     args_value.update(cls._defined_arg_groups[arg_group](id, *extra_args, **extra_kwargs))
        args_value.update(RequestArgGroup(cls.request_arg_group)(id, *extra_args, **extra_kwargs))
        args_value.update(ItemArgGroup(cls.item_arg_group)(id, *extra_args, _item_type=cls.__name__, **extra_kwargs))
        if 'id' not in args_value:
            args_value['id'] = id
        cls._logger.info(f"item created with args:\n{repr(args_value)}")
        return Item(AttrDict(args_value), cls._generate)

    @classmethod
    def _generate(cls, item: Any, result: Any) -> None:
        """
            You need to parse the result first, then generate new items of some `ItemType`s.

            New items should be added directly through class method `_add_item` of other `ItemType`s. This function should not return anything.
            
            Note that you should add new items in reversed order. Because `item`s will be fetched from the end of the queue, so that the newly added `item`s will be processed first.
        """
        # NewItemType._add_items(new_ids_parsed_from_result)
        pass
    # SUBCLASS
    
    @classmethod
    def _add_items(cls, ids, *extra_args, **extra_kwargs) -> None:
        """
            Add new items to `RootQueue`.
        """
        lock = get_global_lock()
        with lock:
            if cls._item_type_register is None:
                RootQueue._lazy_init()
            if cls.__name__ not in cls._item_type_register:
                cls._item_type_register[cls.__name__] = cls
        for id in ids[::-1]:  # add new items in reversed order
            # item = cls(id, *extra_args, **extra_kwargs)
            # item.pend()     # type: ignore # now the item is of type `Item` but not `ItemType`
            cls._add((cls.__name__, id, extra_args, extra_kwargs))  # add items to root queue

    # @classmethod
    # def register(cls):
    #     cls._item_type_register[cls.__name__] = cls
        
    @classmethod
    def __repr__(cls):
        return f"{cls.__name__}({repr(cls._defined_arg_groups)})"


class _ItemType(ItemType):
    _name: str = '_itemtype'
    
    request_arg_group: dict = {}
    item_arg_group: dict = {}

    requestor_args: dict = {}
    middleware_args: dict = {}
    session_args: dict = {}
    
    # include those in your subclass `ItemType` if you want to use its own `logger`
    _logger = None      # OPTIONAL[SUBCLASS]

    @classmethod
    def _generate(cls, item: Any, result: Any) -> None:
        ...


# ------------------------------------ Module Postprocess ------------------------------------ #

logger.info(f"module {__name__} imported")