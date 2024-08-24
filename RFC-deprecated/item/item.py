# import weakref
# from weakref import ref
from time import time
from typing import Any, Callable, Dict
# from tqdm import tqdm

from ..utils.ds import AttrDict
from ..utils.cls import (
    RootType,
    LoggerWrapper
)
from ..utils.defs import (
    PENDING,
    PROCESSING,
    FAILED,
    FINISHED,
    GENERATING,
    _itemStatusToName,
    Process,
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


# class Item(AttrDict, RootType):
class Item(AttrDict):
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
        # if 'id' not in args:
        #     raise ValueError(f"no id in {repr(args)}, which is required for items")
        # if 'bloodline' not in args:
        #     raise ValueError(f"no bloodline in {repr(args)}, which is required for items")
        # if 'save_dir' not in args:
        #     raise ValueError(f"no save_dir in {repr(args)}, which is required for items")
        super().__init__(args)
        # self._get_logger_self(name=f"{self.bloodline[-1][0]}({repr(self.bloodline[-1][1])})", log_path=self.save_dir, level='info', delay=False)  # type: ignore
        # Item._get_logger(__name__, level='debug', propagate=False, add_file_handler=True)  # handlers will be lost after adding to mp.manager.list()
        # self._wrapped_logger = LoggerWrapper(logger=Item._logger, name=f"{self.bloodline[-1][0]}({repr(self.bloodline[-1][1])})", log_path=self.save_dir)
        # self._wrapped_logger = Item._logger
        # self._wrapped_logger = self._logger
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
        # self._wrapped_logger.info(f"status updated from {repr(_itemStatusToName[self._status] if self._status is not None else None)} to {repr(_itemStatusToName[status])}")  
        self._status = status
        
    # def _lazy_init(self):
    #     self._wrapped_logger.lazy_init()
        
    def pend(self):
        # self._lazy_init()
        self._update_status(PENDING)
        
    def process(self):
        self._update_status(PROCESSING)
        
    def finish(self, is_ok: bool, result: Any=None):
        
        def _reduce_active_item_count():
            with get_global_lock():
                RootQueue._active_item_count.value -= 1  # item finished
        
        def _quit():
            # self._wrapped_logger.close()
            _reduce_active_item_count()
                
        if not is_ok:
            self._update_status(FAILED)
            _quit()
            return
        if self.is_leaf:
            self._update_status(FINISHED)
            _quit()
            return
        self._update_status(GENERATING)
        try:
            self._generate(item=self, result=result)
        except Exception as e:
            self._update_status(FAILED)
            _quit()  # must be placed after generating new items
            raise e
        else:
            self._update_status(FINISHED)
        _quit()


class ItemTypeMeta(type):
    def __new__(cls, clsname, bases, attrs):
        # for name, val in attrs.items():
        #     if not isinstance(val, dict) or name not in cls.keyword:
        #         continue
        #     inherited_dict = {}
        #     for base in bases:
        #         if hasattr(base, name):
        #             inherited_dict.update(getattr(base, name))
        #     inherited_dict.update(val)
        #     attrs[name] = inherited_dict
        new_cls = super().__new__(cls, clsname, bases, attrs)
        new_cls._get_logger(__name__, level='info')
        new_cls.register(new_cls.middleware_args)
        return new_cls


class ItemType(RootQueue, Entry, metaclass=ItemTypeMeta):
    """
        `ItemType` serves as the unit of requesting, which is normally responsible for a repetitious kind of a crawler target, such as pages of a website, or a specific kind of API.
        
        When trying to crawl a whole website, there can be many such intermediate targets organized in a tree-like structure, and `ItemType` can be regarded as the representation of each node in the tree.
        
        `ItemType` should not be instantiated, you should subclass it and define `ArgGroup`s in class definition.
    """
    _name: str = 'itemtype'  # SUBCLASS

    request_arg_group: dict = {}  # : RequestArgGroup = RequestArgGroup()  # SUBCLASS
    item_arg_group: dict = {}  # : ItemArgGroup = ItemArgGroup()           # SUBCLASS
    
    requestor_args: dict = {}  # : RequestorArgs = RequestorArgs()         # SUBCLASS
    middleware_args: dict = {}  # : dict[str, MiddlewareArgs] = {}         # SUBCLASS
    session_args: dict = {}  # : SessionArgs = SessionArgs(lib='not_set')  # SUBCLASS

    _logger = None          # OPTIONAL[SUBCLASS]

    def __new__(cls, id, *extra_args, **extra_kwargs):
        """
            Call `ArgGroup`s in this `ItemType`.
        """
        args_value = extra_kwargs
        args_value.update(cls._request_arg_group(id, *extra_args, **extra_kwargs))
        args_value.update(cls._item_arg_group(id, *extra_args, _item_type=cls.__name__, **extra_kwargs))
        # if 'id' not in args_value:
        args_value['id'] = id
        # cls._logger.info(f"item created with args:\n{repr(args_value)}")
        return Item(AttrDict(args_value), cls._generate)

    @classmethod
    def _generate(cls, item: Any, result: Any) -> None:
        """
            You need to parse the result first, then generate new items of some `ItemType`s.

            New items should be added directly through class method `_add_item` of other `ItemType`s. This function should not return anything.
            
            Note that you should add new items in reversed order. Because `item`s will be fetched from the end of the queue, so that the newly added `item`s will be processed first.
        """
        raise NotImplementedError(f"method `_generate` not implemented in {cls.__name__}")
    # SUBCLASS
    
    @classmethod
    def _add_items_single_process(cls, ids, items_kwargs, extra_args, extra_kwargs) -> None:

        def _reduce_active_adder_count():
            with get_global_lock():
                RootQueue._active_adder_count.value -= 1  # item finished
        
        try:
            for id in ids[::-1]:  # add new items in reversed order
                _extra_kwargs = items_kwargs.pop(-1) if items_kwargs is not None else {}
                _extra_kwargs.update(extra_kwargs)
                RootQueue.add(cls(id, *extra_args, **_extra_kwargs))  # add items to root queue
        except Exception as e:
            _reduce_active_adder_count()
            raise e
        _reduce_active_adder_count()

    @classmethod
    def _add_items(cls, ids, items_kwargs=None, *extra_args, **extra_kwargs) -> None:  # must be executed after starting RootQueue
        """
            Add new items to `RootQueue`.
        """
        def _isiterable(x):
            try:
                iter(x)
                return True
            except TypeError:
                return False
            
        def _convert_to_list(x):
            if not isinstance(x, list):
                if _isiterable(x):
                    if isinstance(x, str) or isinstance(x, dict) or isinstance(x, set):
                        x = [x]
                    else:
                        x = list(x)
                else:
                    x = [x]
            return x
            
        ids = _convert_to_list(ids)
        if items_kwargs is not None:
            items_kwargs = _convert_to_list(items_kwargs)
            if len(items_kwargs) != len(ids):
                cls._logger.error(f"length of items_kwargs {len(items_kwargs)} not equal to length of ids {len(ids)}")
                assert False

        if 'bloodline' not in extra_kwargs:
           cls._logger.warning(f"no bloodline found in {repr(extra_kwargs)}, which is required for items\nif this is the root item, you should pass `bloodline=[]` when adding items\notherwise, in most cases, you should pass `bloodline=item.bloodline`")
    
        processes = []
        nproc = min(1, cls.requestor_args['nproc'])
        n_ids = len(ids)
        cls._request_arg_group = RequestArgGroup(cls.request_arg_group)
        cls._item_arg_group = ItemArgGroup(cls.item_arg_group)
        with get_global_lock():
            if not RootQueue._initialized:
                RootQueue.lazy_init()
            RootQueue._active_adder_count.value += nproc  # must add this value in advance
        for i in range(nproc):
            lower_n_ids = n_ids * i // nproc
            upper_n_ids = n_ids * (i + 1) // nproc
            items_kwargs = items_kwargs[lower_n_ids:upper_n_ids] if items_kwargs is not None else None
            # items = [cls(id, *extra_args, **{**items_kwarg, **extra_kwargs}) for id, items_kwarg in tqdm(zip(ids, items_kwargs))]
            # print(len(items))
            # exit(0)
            processes.append(Process(target=cls._add_items_single_process, args=(ids[lower_n_ids:upper_n_ids], items_kwargs, extra_args, extra_kwargs)))
            processes[i].start()
        
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