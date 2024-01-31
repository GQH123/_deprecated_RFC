import random

from ..utils.cls import RootType
from ..args.arg_group import (
    RequestorArgs,
    SessionArgs,
)
from ..req.middleware import get_middleware
from ..req.session import get_session
from ..req.requestor import Requestor
from ..utils.log import get_logger

logger = get_logger(__name__)
logger.info(f"importing module {__name__}")


class Entry(RootType):
    _name: str = 'entry'
    
    # requestor_args: RequestorArgs = RequestorArgs()           # SUBCLASS in `ItemType`
    # middleware_args: dict[str, MiddlewareArgs] = {}           # SUBCLASS in `ItemType`
    # session_args: SessionArgs = SessionArgs(lib='not_set')    # SUBCLASS in `ItemType
    
    _started: bool = False
    # _logger = None  # _logger should be defined in `ItemType`
    
    @classmethod
    def start(cls, ids=[], *extra_args, **extra_kwargs) -> None:
        """
            Start crawling with given `ids`. This is the MAIN ENTRY of the RFC, which I decided to place in `ItemType`. So in fact `ItemType` is the most important class in RFC. With such design, you could only import `ItemType`, subclass it to make your new `ItemType`s, and call its `start` method to start crawling, without accessing to any other RFC modules.
            
            `ItemType` can only be started once. You should call `start` method only on your entry `ItemType`.
        """
        if cls._logger is None:
            cls._get_logger(__name__, level='info')
        if cls._started:
            cls._logger.warning(f"{repr(cls)} has already been started, cannot start again")
            return
        try:
            # if not isinstance(ids, list):
            #     ids = list(ids)
            # if debug_n is not None:
            #     cls._logger.info(f"debug mode, only {debug_n} randomly selected items will be crawled")
            #     random.shuffle(ids)
            #     ids = ids[:debug_n]
            cls._session = get_session(SessionArgs(cls.session_args), cls._logger)
            cls._middleware = get_middleware(cls.middleware_args, cls._logger)
            cls._requestor = Requestor(cls._session, cls._middleware, RequestorArgs(cls.requestor_args))
        except Exception as e:
            error_report = f'[{repr(type(e).__name__)}] {repr(e)}'
            cls._logger.error(f"{repr(cls)} failed to start, caught error {error_report}")
            raise e
        cls._lazy_init()
        cls._add_items(ids, *extra_args, **extra_kwargs)
        cls._started = True
        cls._logger.info(f"{repr(cls)} started")
        cls._requestor.run()


# ------------------------------------ Module Postprocess ------------------------------------ #

logger.info(f"module {__name__} imported")