from RFC.utils.functional_utils import log, save_object

from .MiddleWare import MiddleWare
from .Save_MiddleWareConfig import Save_MiddleWareConfig


class Save_MiddleWare(MiddleWare):
    def _init_attr(
        self,
        middleware_config: Save_MiddleWareConfig,
    ):
        super()._init_attr(middleware_config)
        self.savename = middleware_config.savename
        self.mode = middleware_config.mode

    def _init_process(
        self,
        middleware_config: Save_MiddleWareConfig,
    ):
        async def save(item, data):
            log(f'saving item {repr(item.name)} -> {repr(self.savename(item))}', ['debug', 'current_requested_item_log'], 'Save_MiddleWare.save', 'info', __name__)
            save_object(data, self.savename(item), 'result', self.mode)
        self.process = save
    
    def _init_error_handler(
        self,
        middleware_config: Save_MiddleWareConfig,
    ):
        async def error_handler(e, item, resp):
            log(f'middleware saving error [{type(e)}] {e}\n', 'current_requested_item_error', 'Save_MiddleWare.save', 'error', __name__, trace=True)
        self.error_handler = error_handler

    def __init__(
        self,
        middleware_config: Save_MiddleWareConfig,
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
            return Save_MiddleWareConfig(**my_attr)
        else:
            return my_attr