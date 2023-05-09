from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import ConditionOverflowError, ParamTypeError, ParamValueError

from .MiddleWareConfig import MiddleWareConfig
from .MiddleWare import MiddleWare
from .JSON_MiddleWareConfig import JSON_MiddleWareConfig
from .JSON_MiddleWare import JSON_MiddleWare

all_supported_middlewares = ['default', 'json']


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
        return MiddleWareConfig(**kwargs)
    elif middleware_config == 'json':
        return JSON_MiddleWareConfig(**kwargs)
    else:
        raise ConditionOverflowError(middleware_config, __name__)


@leaf(system=True)
def get_middleware(
    middleware_config: MiddleWareConfig | str,
    **kwargs,
):
    if isinstance(middleware_config, str):
        middleware_type = middleware_config
        middleware_config = get_middleware_config(middleware_type, **kwargs)
    else:
        middleware_type = type(middleware_config).__name__
        if middleware_type == 'MiddleWareConfig':
            middleware_type = 'default'
        elif middleware_type == 'JSON_MiddleWareConfig':
            middleware_type = 'json'
        else:
            raise ParamTypeError('middleware_config', middleware_config, [MiddleWareConfig], __name__)

    if middleware_type not in all_supported_middlewares:
        raise ParamValueError('middleware_type', middleware_type, all_supported_middlewares, __name__)
    if middleware_type == 'default':
        return MiddleWare(middleware_config)
    elif middleware_type == 'json':
        return JSON_MiddleWare(middleware_config)
    else:
        raise ConditionOverflowError(middleware_type, __name__)


leaves = get_leaves()