from .MiddleWare import MiddleWare
from .StatusCodeMiddleWareConfig import StatusCodeMiddleWareConfig as MiddleWareConfig
from .MiddleWare_Exceptions import MiddleWare_UnexpectedStatusCode
from .MiddleWare_Functional_Utils import get_status_code

class StatusCodeMiddleWare(MiddleWare):
    def _init_attr(
        self,
        middleware_config: MiddleWareConfig,
    ):
        super()._init_attr(middleware_config)
        self.expected_status_codes = middleware_config.expected_status_codes
        self.strict = middleware_config.strict

    def _init_process(
        self,
        middleware_config: MiddleWareConfig,
    ):
        async def parse_status_code(item, resp):
            status_code = get_status_code(resp, self.framework)
            expected_status_codes = self.expected_status_codes
            if status_code in expected_status_codes:
                return resp
            else:
                e = MiddleWare_UnexpectedStatusCode(status_code, expected_status_codes)
                if self.strict:
                    raise e
                else:
                    self.error_logger(f'unexpected status code [{type(e)}] {e}\n', 'StatusCodeMiddleWare.parse_status_code')
                    return resp
        self.process = parse_status_code

    def _init_error_handler(
        self,
        middleware_config: MiddleWareConfig,
    ):
        async def unexpected_status_code(e, item, resp):
            self.error_logger(f'unexpected status code [{type(e)}] {e}\n', 'StatusCodeMiddleWare.parse_status_code')
            return e
        self.error_handler = unexpected_status_code

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
        my_attr['expected_status_codes'] = self.expected_status_codes
        my_attr['strict'] = self.strict
        if return_config:
            return MiddleWareConfig(**my_attr)
        else:
            return my_attr