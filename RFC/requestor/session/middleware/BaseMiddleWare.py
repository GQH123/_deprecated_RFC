from RFC.itemset.RawItemset import RawItem
from RFC.utils.BaseModule import BaseModule
from RFC.utils.exception_utils import NotSupported, ConditionOverflowError

from .BaseMiddleWareConfig import BaseMiddleWareConfig


class BaseMiddleWare(BaseModule):
    def _init_attr(
        self,
        middleware_config: BaseMiddleWareConfig,
    ):
        self.framework = middleware_config.framework

    def _init_process(
        self,
        middleware_config: BaseMiddleWareConfig,
    ):
        async def return_raw(resp):
            return resp
        self.process = return_raw

    def _init_error_handler(
        self,
        middleware_config: BaseMiddleWareConfig,
    ):
        async def raise_error(e, x):
            raise e
        self.error_handler = raise_error

    def __init__(
        self,
        middleware_config: BaseMiddleWareConfig,
    ):
        super().__init__(middleware_config)
        self._init_attr(middleware_config=middleware_config)
        self._init_process(middleware_config=middleware_config)
        self._init_error_handler(middleware_config=middleware_config)

    async def __process__(
        self,
        item: RawItem,
    ):
        try:
            return await self.process(item), True
        except Exception as e:
            return await self.error_handler(e, item), False
    
    def _retrieve_config(
        self,
        return_config: bool = False
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        my_attr.update({
            'framework': self.framework,
        })
        if return_config:
            return BaseMiddleWareConfig(**my_attr)
        else:
            return my_attr