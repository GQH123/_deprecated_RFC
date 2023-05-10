from .MiddleWare import MiddleWare
from .JSONMiddleWareConfig import JSONMiddleWareConfig
from .MiddleWare_Functional_Utils import return_json


class JSONMiddleWare(MiddleWare):
    def _init_attr(
        self,
        middleware_config: JSONMiddleWareConfig,
    ):
        super()._init_attr(middleware_config)

    def _init_process(
        self,
        middleware_config: JSONMiddleWareConfig,
    ):
        async def _return_json(item, resp):
            return await return_json(resp, self.framework)
        self.process = _return_json

    def _init_error_handler(
        self,
        middleware_config: JSONMiddleWareConfig,
    ):
        async def error_handler(e, item, resp):
            if type(e).__name__ == 'MiddleWare_UnknownFramework':
                self.error_logger(f'middleware encountered unknown framework {repr(self.framework)}', 'JSONMiddleWare.return_json')
            else:
                self.error_logger(f'middleware error [{type(e)}] {e}', 'JSONMiddleWare.return_json')
            return e
        self.error_handler = error_handler

    def __init__(
        self,
        middleware_config: JSONMiddleWareConfig,
    ):
        super().__init__(middleware_config)
    
    def _retrieve_config(
        self,
        return_config: bool = False
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        if return_config:
            return JSONMiddleWareConfig(**my_attr)
        else:
            return my_attr