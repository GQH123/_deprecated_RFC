from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import ConditionOverflowError, ParamTypeError, ParamValueError

from .MiddleWareConfig import MiddleWareConfig
from .MiddleWare import MiddleWare
from .JSONMiddleWareConfig import JSONMiddleWareConfig
from .JSONMiddleWare import JSONMiddleWare
from .StatusCodeMiddleWareConfig import StatusCodeMiddleWareConfig
from .StatusCodeMiddleWare import StatusCodeMiddleWare
from .SaveMiddleWareConfig import SaveMiddleWareConfig
from .SaveMiddleWare import SaveMiddleWare
from .SaveBinaryMiddleWareConfig import SaveBinaryMiddleWareConfig
from .SaveBinaryMiddleWare import SaveBinaryMiddleWare


all_supported_middlewares = ['default', 'json', 'binary', 'statuscode', 'save']


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
        return JSONMiddleWareConfig(**kwargs)
    elif middleware_config == 'binary':
        return SaveBinaryMiddleWareConfig(**kwargs)
    elif middleware_config == 'statuscode':
        return StatusCodeMiddleWareConfig(**kwargs)
    elif middleware_config == 'save':
        return SaveMiddleWareConfig(**kwargs)
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
        elif middleware_type == 'JSONMiddleWareConfig':
            middleware_type = 'json'
        elif middleware_type == 'StatusCodeMiddleWareConfig':
            middleware_type = 'statuscode'
        elif middleware_type == 'SaveBinaryMiddleWareConfig':
            middleware_type = 'binary'
        elif middleware_type == 'SaveMiddleWareConfig':
            middleware_type = 'save'
        else:
            raise ParamTypeError('middleware_config', middleware_config, [MiddleWareConfig], __name__)

    if middleware_type not in all_supported_middlewares:
        raise ParamValueError('middleware_type', middleware_type, all_supported_middlewares, __name__)
    if middleware_type == 'default':
        return MiddleWare(middleware_config)
    elif middleware_type == 'json':
        return JSONMiddleWare(middleware_config)
    elif middleware_type == 'binary':
        return SaveBinaryMiddleWare(middleware_config)
    elif middleware_type == 'statuscode':
        return StatusCodeMiddleWare(middleware_config)
    elif middleware_type == 'save':
        return SaveMiddleWare(middleware_config)
    else:
        raise ConditionOverflowError(middleware_type, __name__)


leaves = get_leaves()