from RFC.utils.functional_utils import save_object

from .MiddleWare import MiddleWare
from .SaveBinaryMiddleWareConfig import SaveBinaryMiddleWareConfig as MiddleWareConfig
from .MiddleWare_Functional_Utils import parse_content_type, parse_content


class SaveBinaryMiddleWare(MiddleWare):
    def _init_attr(
        self,
        middleware_config: MiddleWareConfig,
    ):
        super()._init_attr(middleware_config)
        self.savename = middleware_config.savename
        self.mode = middleware_config.mode

    def _init_process(
        self,
        middleware_config: MiddleWareConfig,
    ):
        async def save_binary(item, resp):
            content_type = parse_content_type(resp, self.framework)
            data_ext = content_type.split('/')[-1]
            content = await parse_content(resp, self.framework)
            self.info_logger(f'saving item {repr(item.name)} -> {repr(self.savename(item, data_ext))}', 'SaveBinaryMiddleWare.save_binary')
            save_object(content, self.savename(item, data_ext), 'result', self.mode)
            return resp
        self.process = save_binary

    def _init_error_handler(
        self,
        middleware_config: MiddleWareConfig,
    ):
        async def error_handler(e, item, resp):
            self.error_logger(f'middleware saving error [{type(e)}] {e}\n', 'SaveBinaryMiddleWare.save_binary')
            return e
        self.error_handler = error_handler

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
        my_attr.update({
            'savename': self.savename,
            'mode': self.mode,
        })
        if return_config:
            return MiddleWareConfig(**my_attr)
        else:
            return my_attr