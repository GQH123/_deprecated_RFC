from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import NotSupported, ConditionOverflowError, ParamTypeError

from .QGNetProxyManager import QGNetProxyManager


launched_managers = {}


@leaf()
def init(**kwargs):
    ...


@leaf(freeze=True)
def off(**kwargs):
    return None


@leaf(freeze=True)
def fixed(value, **kwargs):
    return value


@leaf()
def passin(proxies, ptype, **kwargs):
    if ptype is dict:
        if isinstance(proxies, dict):
            return proxies 
        else:
            raise ParamTypeError('proxies', proxies, dict, __name__)
    elif ptype is str:
        if isinstance(proxies, str):
            return proxies 
        elif isinstance(proxies, dict):
            return proxies['http']
        else:
            raise ParamTypeError('proxies', proxies, str, __name__)

    raise ParamTypeError('proxies', proxies, [dict, str], __name__)


@leaf()
def login(pm_type, **kwargs):
    all_supported_proxy_type = ['QGNet']
    if pm_type not in all_supported_proxy_type:
        raise NotSupported('pm_type', pm_type, all_supported_proxy_type, __name__)

    if pm_type not in launched_managers:
        if pm_type == 'QGNet':
            launched_managers[pm_type] = QGNetProxyManager(**kwargs)
        else:
            raise ConditionOverflowError(pm_type, __name__)
    return launched_managers[pm_type].apply()


leaves = get_leaves()