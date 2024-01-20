from .BaseMiddleWare import BaseMiddleWare
from .MiddleWareConfig import MiddleWareConfig as MiddleWareConfig


class MiddleWare(BaseMiddleWare):
    def _init_attr(
        self,
        middleware_config: MiddleWareConfig,
    ):
        super()._init_attr(middleware_config)
        ... # remember to add specific attributes to self

    def _init_process(
        self,
        middleware_config: MiddleWareConfig,
    ):
        async def return_raw(item, resp):  # pay attention, entry must be async
            return resp
        self.process = return_raw

    def _init_error_handler(
        self,
        middleware_config: MiddleWareConfig,
    ):
        async def raise_error(e, item, resp):  # pay attention, entry must be async
            return e
        self.error_handler = raise_error

    def __init__(
        self,
        middleware_config: MiddleWareConfig,
    ):
        super().__init__(middleware_config)
    
    def _retrieve_config(
        self,
        return_config: bool = False
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        ... # remember to add specific attributes to my_attr
        if return_config:
            return MiddleWareConfig(**my_attr)
        else:
            return my_attr