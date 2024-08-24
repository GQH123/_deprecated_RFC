import multiprocessing as mp

from ..utils.cls import RootType
from ..args.arg_group import (
    RequestorArgs,
    SessionArgs,
)
from ..req.middleware import get_middleware
from ..req.session import get_session
from ..req.requestor import Requestor
from ..utils.log import get_logger

from .queue import RootQueue

logger = get_logger(__name__)
logger.info(f"importing module {__name__}")


class Entry(RootType):
    _name: str = 'entry'
    
    _started: bool = False
    _registered_itemtypes = {}
    _logger = None
    
    @classmethod
    def register(item_type, middleware_args):  # now only `middleware_args` is required
        # no item_type type checking due to circular importing
        Entry._registered_itemtypes[item_type.__name__] = (middleware_args, item_type._logger)

    @classmethod
    def start(item_type, ids=[], items_kwargs=None, *extra_args, **extra_kwargs) -> None:
        """
            Start crawling with given `ids`. This is the MAIN ENTRY of the RFC, which I decided to place in `ItemType`. So in fact `ItemType` is the most important class in RFC. With such design, you could only import `ItemType`, subclass it to make your new `ItemType`s, and call its `start` method to start crawling, without accessing to any other RFC modules.
            
            `ItemType` can only be started once. You should call `start` method only on your entry `ItemType`.
        """
        if Entry._logger is None:
            Entry._get_logger(__name__, level='info')
        if Entry._started:
            Entry._logger.warning(f"{repr(item_type)} has already been started, cannot start again")
            return
        try:
            _middlewares = {}
            _session = get_session(SessionArgs(item_type.session_args), item_type._logger)
            for item_type_name, (middleware_args, _logger) in Entry._registered_itemtypes.items():
                _middlewares[item_type_name] = get_middleware(middleware_args, _logger)
            Entry._requestor = Requestor(_session, _middlewares, RequestorArgs(item_type.requestor_args))
        except Exception as e:
            error_report = f'[{repr(type(e).__name__)}] {repr(e)}'
            item_type._logger.error(f"{repr(item_type)} failed to start, caught error {error_report}")
            raise e
        if not RootQueue._initialized:
            RootQueue.lazy_init()
        item_type._add_items(ids, items_kwargs, *extra_args, **extra_kwargs)
        
        # start root queue reporter
        Entry._started = True
        item_type._logger.info(f"{repr(item_type)} started")
        RootQueue_reporter = mp.Process(target=RootQueue.report)
        RootQueue_reporter.start()
        
        # run requestor
        Entry._requestor.run()  # blocked until all items finished
        RootQueue_reporter.join()
        Entry._logger.info(f"FINISHED")


# ------------------------------------ Module Postprocess ------------------------------------ #

logger.info(f"module {__name__} imported")