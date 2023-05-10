from RFC.utils.functional_utils import log, save_object

from .MiddleWare import MiddleWare
from .JSON_MiddleWareConfig import JSON_MiddleWareConfig
from .Exceptions import MiddleWare_UnknownFramework


class JSON_MiddleWare(MiddleWare):
    def _init_attr(
        self,
        middleware_config: JSON_MiddleWareConfig,
    ):
        super()._init_attr(middleware_config)

    def _init_process(
        self,
        middleware_config: JSON_MiddleWareConfig,
    ):
        async def return_json(item, resp):
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
        async def error_handler(e, item, resp):
            if type(e).__name__ == 'MiddleWare_UnknownFramework':
                self.error_logger(f'middleware encountered unknown framework {repr(self.framework)}', 'JSON_MiddleWare.return_json')
            else:
                self.error_logger(f'middleware error [{type(e)}] {e}', 'JSON_MiddleWare.return_json')
        self.error_handler = error_handler

    def __init__(
        self,
        middleware_config: JSON_MiddleWareConfig,
    ):
        super().__init__(middleware_config)
    
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