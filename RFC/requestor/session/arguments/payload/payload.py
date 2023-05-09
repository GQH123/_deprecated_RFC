from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import ParamTypeError


@leaf()
def init(**kwargs):
    ...


def basic(payload, ptype, **kwargs):
    if not isinstance(payload, ptype):
        raise ParamTypeError('payload', payload, ptype, __name__)
    return payload


@leaf(freeze=True)
def fixed(payload, ptype, **kwargs):
    if payload is None:
        return None
    return basic(payload, ptype, **kwargs)


@leaf()
def passin(payload, ptype, **kwargs):
    if payload is None:
        return None
    return basic(payload, ptype, **kwargs)


leaves = get_leaves()