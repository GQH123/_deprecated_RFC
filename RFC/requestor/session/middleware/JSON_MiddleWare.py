from .MiddleWare import MiddleWare
from .JSON_MiddleWareConfig import JSON_MiddleWareConfig
from .Exceptions import MiddleWare_UnknownFramework

from RFC.utils.functional_utils import log


class JSON_MiddleWare(MiddleWare):
    def _init_process(
        self,
        middleware_config: JSON_MiddleWareConfig,
    ):
        async def return_json(resp):
            if self.framework == 'requests':
                return resp.json()
            elif self.framework == 'aiohttp':
                return await resp.json() 
            elif self.framework == 'asks':
                return resp.json()
            else:
                raise MiddleWare_UnknownFramework(self.framework)

        self.process = return_json

    def _init_error_handler(
        self,
        middleware_config: JSON_MiddleWareConfig,
    ):
        async def error_handler(e, x):
            if type(e).__name__ == 'MiddleWare_UnknownFramework':
                log('encountered unknown framework', 'current_requested_item_log', 'JSON_MiddleWare', 'error', __name__)
            else:
                log('json decoding error', 'current_requested_item_log', 'JSON_MiddleWare', 'error', __name__)

        self.error_handler = error_handler

    def __init__(
        self,
        middleware_config: JSON_MiddleWareConfig,
    ):
        super().__init__(middleware_config=middleware_config)
    
    def _retrieve_config(
        self,
        return_config: bool = False
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        if return_config:
            return JSON_MiddleWareConfig(**my_attr)
        else:
            return my_attr