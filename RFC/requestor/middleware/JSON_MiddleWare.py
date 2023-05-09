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
        self.savename = middleware_config.savename
        self.mode = middleware_config.mode

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
        
        async def save(item, resp):
            log(f'saving {item.name} -> {self.savename(item)}', 'current_requested_item_log', 'JSON_MiddleWare.save', 'info', __name__)
            json = await return_json(item, resp)
            save_object(json, self.savename(item), 'result', self.mode)

        self.process = save

    def _init_error_handler(
        self,
        middleware_config: JSON_MiddleWareConfig,
    ):
        async def error_handler(e, item, resp):
            if type(e).__name__ == 'MiddleWare_UnknownFramework':
                log('middleware encountered unknown framework', 'current_requested_item_error', 'JSON_MiddleWare.__call__.json', 'error', __name__, trace=True)
            elif type(e).__name__ == 'SavingError':
                log(f'middleware saving error [{type(e)}] {e}\n', 'current_requested_item_error', 'JSON_MiddleWare.__call__.save', 'error', __name__, trace=True)
            else:
                log(f'middleware error [{type(e)}] {e}', 'current_requested_item_error', 'JSON_MiddleWare.__call__.json', 'error', __name__, trace=True)

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
        my_attr.update({
            'savename': self.savename,
            'mode': self.mode,
        })
        if return_config:
            return JSON_MiddleWareConfig(**my_attr)
        else:
            return my_attr