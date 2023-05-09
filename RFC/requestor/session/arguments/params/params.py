from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import ParamTypeError


@leaf()
def init(**kwargs):
    ...


def basic(params, ptype, **kwargs):
    if not isinstance(params, ptype):
        raise ParamTypeError('params', params, ptype, __name__)
    return params


@leaf(freeze=True)
def fixed(params, ptype, **kwargs):
    if params is None:
        return None
    return basic(params, ptype, **kwargs)


@leaf()
def passin(params, ptype, **kwargs):
    if params is None:
        return None
    return basic(params, ptype, **kwargs)


leaves = get_leaves()