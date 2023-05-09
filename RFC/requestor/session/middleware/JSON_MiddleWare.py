from .MiddleWare import MiddleWare
from .JSON_MiddleWareConfig import JSON_MiddleWareConfig
from .Exceptions import MiddleWare_UnknownFramework


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
                print('MiddleWare_UnknownFramework

        self.error_handler = error_handler

    def __init__(
        self,
        middleware_config: JSON_MiddleWareConfig,
    ):
        super().__init__(middleware_config=middleware_config)