from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import ConditionOverflowError, ParamTypeError, ParamValueError

from .RequestorConfig import RequestorConfig
from .Requestor import Requestor

all_supported_requestors = ['default']


@leaf()
def init(**kwargs):
    ...


def get_requestor_config(
    requestor_type: str,
    **kwargs,
):
    if requestor_type not in all_supported_requestors:
        raise ParamValueError('requestor_type', requestor_type, all_supported_requestors, __name__)
    if requestor_type == 'default':
        return RequestorConfig()
    else:
        raise ConditionOverflowError(requestor_type, __name__)


@leaf(system=True)
def get_requestor(
    requestor_config: RequestorConfig | str,
    **kwargs,
):
    if isinstance(requestor_config, str):
        requstor_type = requestor_config
        requestor_config = get_requestor_config(requstor_type, **kwargs)
    else:
        requstor_type = type(requestor_config).__name__
        if requstor_type == 'RequestorConfig':
            requstor_type = 'default'
        else:
            raise ParamTypeError('requestor_config', requestor_config, [RequestorConfig], __name__)

    if requstor_type not in all_supported_requestors:
        raise ParamValueError('requestor_type', requstor_type, all_supported_requestors, __name__)
    if requstor_type == 'default':
        return Requestor(requestor_config, **kwargs)
    else:
        raise ConditionOverflowError(requstor_type, __name__)


leaves = get_leaves()