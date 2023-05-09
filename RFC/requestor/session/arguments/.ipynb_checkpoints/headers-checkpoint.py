from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import NotSupportedError, ConditionOverflowError

from .HeadersConfig import HeadersConfig
from .MyProxyHeadersConfig import MyProxyHeadersConfig
from .Headers import Headers


@leaf()
def init(**kwargs):
    ...


def get_headers_config(
    headers_config: str
):
    all_supported_headers_configs = ['default', 'my_proxy']
    if headers_config not in all_supported_headers_configs:
        raise NotSupportedError(headers_config, all_supported_headers_configs, __name__)
    if headers_config == 'default':
        return HeadersConfig()
    elif headers_config == 'my_proxy':
        return MyProxyHeadersConfig()
    else:
        raise ConditionOverflowError(headers_config, __name__)


@leaf(system=True)
def get_headers(
    headers_type: str,
    headers_config: HeadersConfig | str,
    **kwargs,
):
    if headers_config is None:
        headers_config = 'default'
    if isinstance(headers_config, str):
        headers_config = get_headers_config(headers_config)

    all_supported_headers = ['default']

    if headers_type not in all_supported_headers:
        raise NotSupportedError(headers_type, all_supported_headers, __name__)
    if headers_type == 'default':
        return Headers(headers_config)
    else:
        raise ConditionOverflowError(headers_type, __name__)


leaves = get_leaves()