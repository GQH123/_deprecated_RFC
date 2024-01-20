from RFC.utils.functional_utils import save_object

from .MiddleWare import MiddleWare
from .SaveMiddleWareConfig import SaveMiddleWareConfig


class SaveMiddleWare(MiddleWare):
    def _init_attr(
        self,
        middleware_config: SaveMiddleWareConfig,
    ):
        super()._init_attr(middleware_config)
        self.savename = middleware_config.savename
        self.mode = middleware_config.mode

    def _init_process(
        self,
        middleware_config: SaveMiddleWareConfig,
    ):
        async def save(item, data):
            self.info_logger(f'saving item {repr(item.name)} -> {repr(self.savename(item))}', 'SaveMiddleWare.save')
            save_object(data, self.savename(item), 'result', self.mode)
            return data
        self.process = save
    
    def _init_error_handler(
        self,
        middleware_config: SaveMiddleWareConfig,
    ):
        async def error_handler(e, item, resp):
            self.error_logger(f'middleware saving error [{type(e)}] {e}\n', 'SaveMiddleWare.save')
            return e
        self.error_handler = error_handler

    def __init__(
        self,
        middleware_config: SaveMiddleWareConfig,
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
            return SaveMiddleWareConfig(**my_attr)
        else:
            return my_attr