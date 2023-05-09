from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import ConditionOverflowError, ParamTypeError, ParamValueError

from .MiddlewareConfig import MiddlewareConfig
from .MiddlewareConfigMyProxy import MiddlewareConfigMyProxy
from .Middleware import Middleware

all_supported_middlewares = ['default', 'my_proxy']


@leaf()
def init(**kwargs):
    ...


def get_middleware_config(
    middleware_config: str,
    **kwargs,
):
    if middleware_config not in all_supported_middlewares:
        raise ParamValueError('middleware_config', middleware_config, all_supported_middlewares, __name__)
    if middleware_config == 'default':
        return MiddlewareConfig()
    elif middleware_config == 'my_proxy':
        return MiddlewareConfigMyProxy()
    else:
        raise ConditionOverflowError(middleware_config, __name__)