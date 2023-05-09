from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import ConditionOverflowError, ParamTypeError, ParamValueError

from .ArgumentsConfig import ArgumentsConfig
from .ArgumentsConfigMyProxy import ArgumentsConfigMyProxy
from .Arguments import Arguments

all_supported_arguments = ['default', 'my_proxy']


@leaf()
def init(**kwargs):
    ...


def get_arguments_config(
    arguments_config: str,
    **kwargs,
):
    if arguments_config not in all_supported_arguments:
        raise ParamValueError('arguments_config', arguments_config, all_supported_arguments, __name__)
    if arguments_config == 'default':
        return ArgumentsConfig()
    elif arguments_config == 'my_proxy':
        return ArgumentsConfigMyProxy()
    else:
        raise ConditionOverflowError(arguments_config, __name__)


@leaf(system=True)
def get_arguments(
    arguments_config: ArgumentsConfig | str,
    **kwargs,
):
    if isinstance(arguments_config, str):
        arguments_type = arguments_config
        arguments_config = get_arguments_config(arguments_type, **kwargs)
    else:
        arguments_type = type(arguments_config).__name__
        if arguments_type == 'ArgumentsConfig':
            arguments_type = 'default'
        elif arguments_type == 'ArgumentsConfigMyProxy':
            arguments_type = 'my_proxy'
        else:
            raise ParamTypeError('arguments_config', arguments_config, [ArgumentsConfig], __name__)

    if arguments_type not in all_supported_arguments:
        raise ParamValueError('arguments_type', arguments_type, all_supported_arguments, __name__)
    if arguments_type == 'default':
        return Arguments(arguments_config, **kwargs)
    elif arguments_type == 'my_proxy':
        return Arguments(arguments_config, **kwargs)
    else:
        raise ConditionOverflowError(arguments_type, __name__)


leaves = get_leaves()