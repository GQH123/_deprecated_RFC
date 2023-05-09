from RFC.itemset.RawItemset import RawItem
from RFC.utils.BaseModule import BaseModule
from RFC.utils.exception_utils import NotSupported, ConditionOverflowError

from .MiddleWareConfig import MiddleWareConfig


class BaseMiddleWare(BaseModule):
    def _init_attr(
        self,
        middleware_config: MiddleWareConfig,
    ):
        self.framework = middleware_config.framework

    def _init_process(
        self,
        middleware_config: MiddleWareConfig,
    ):
        async def return_raw(resp):
            return resp
        self.process = return_raw

    def _init_error_handler(
        self,
        middleware_config: MiddleWareConfig,
    ):
        async def raise_error(e, x):
            raise e
        self.error_handler = raise_error

    def __init__(
        self,
        middleware_config: MiddleWareConfig,
    ):
        self.middleware_config = middleware_config
        self.name = middleware_config.name
        self._init_attr(middleware_config=middleware_config)
        self._init_process(middleware_config=middleware_config)
        self._init_error_handler(middleware_config=middleware_config)

    async def __process__(
        self,
        item: RawItem,
    ):
        try:
            return await self.process(item)
        except Exception as e:
            return await self.error_handler(e, item)