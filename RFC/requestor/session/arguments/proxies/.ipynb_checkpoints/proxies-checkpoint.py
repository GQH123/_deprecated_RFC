from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import NotSupportedError, ConditionOverflowError

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
def login(pm_type, **kwargs):
    all_supported_proxy_type = ['QGNet']
    if pm_type not in all_supported_proxy_type:
        raise NotSupportedError(pm_type, all_supported_proxy_type, __name__)

    if pm_type not in launched_managers:
        if pm_type == 'QGNet':
            launched_managers[pm_type] = QGNetProxyManager(**kwargs)
        else:
            raise ConditionOverflowError(pm_type, __name__)
    return launched_managers[pm_type].apply()


leaves = get_leaves()