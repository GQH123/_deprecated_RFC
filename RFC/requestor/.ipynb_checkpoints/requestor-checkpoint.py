from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import NotSupportedError, ConditionOverflowError

from .RequestorConfig import RequestorConfig
from .Requestor import Requestor


@leaf()
def init(**kwargs):
    ...


def get_requestor_config(
    requestor_config: str
):
    all_supported_requestor_configs = ['default']
    if requestor_config not in all_supported_requestor_configs:
        raise NotSupportedError(requestor_config, all_supported_requestor_configs, __name__)
    if requestor_config == 'default':
        return RequestorConfig()
    else:
        raise ConditionOverflowError(requestor_config, __name__)


@leaf(system=True)
def get_requestor(
    requestor_type: str,
    requestor_config: RequestorConfig | str,
    **kwargs,
):
    if requestor_config is None:
        requestor_config = 'default'
    if isinstance(requestor_config, str):
        requestor_config = get_requestor_config(requestor_config)

    all_supported_requestors = ['default']

    if requestor_type not in all_supported_requestors:
        raise NotSupportedError(requestor_type, all_supported_requestors, __name__)
    if requestor_type == 'default':
        return Requestor(requestor_config)
    else:
        raise ConditionOverflowError(requestor_type, __name__)


leaves = get_leaves()