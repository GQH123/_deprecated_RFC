from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import NotSupportedError, ConditionOverflowError


@leaf()
def init(**kwargs):
    ...


def cookies_to_str(cookies, sep='; ', **kwargs):
    all_supported_ctypes = [str, dict]
    ctype = type(cookies)
    if ctype not in all_supported_ctypes:
        raise NotSupportedError(ctype, all_supported_ctypes, __name__)
    if isinstance(cookies, str):
        return cookies
    elif isinstance(cookies, dict):
        cookies = sep.join([f'{k}={v}' for k, v in cookies.items()])
        return cookies
    else:
        raise ConditionOverflowError(ctype, __name__)


def cookies_to_dict(cookies, sep='; ', cont='=', **kwargs):
    all_supported_ctypes = [str, dict]
    ctype = type(cookies)
    if ctype not in all_supported_ctypes:
        raise NotSupportedError(ctype, all_supported_ctypes, __name__)
    if isinstance(cookies, dict):
        return cookies
    elif isinstance(cookies, str):
        cookies = {k_v.split(cont)[0]: cont.join(k_v.split(cont)[1:]) for k_v in cookies.split(sep)}
        return cookies
    else:
        raise ConditionOverflowError(ctype, __name__)


def cookies_converter(cookies, ctype, **kwargs):
    all_supported_ctypes = [str, dict]
    if ctype not in all_supported_ctypes:
        raise NotSupportedError(ctype, all_supported_ctypes, __name__)
    if isinstance(cookies, dict):
        return cookies_to_dict(cookies, **kwargs)
    elif isinstance(cookies, str):
        return cookies_to_str(cookies, **kwargs)
    else:
        raise ConditionOverflowError(ctype, __name__)


@leaf()
def passin(cookies, ctype, **kwargs):
    return cookies_converter(cookies, ctype, **kwargs)


@leaf()
def read_from_file(cookies_file, rank, **kwargs):
    sep = kwargs.get('sep', '\n')
    with open(cookies_file, 'r') as f:
        cookies = [cookies for cookies in f.read().split(sep) if cookies]

    if len(cookies) <= rank:
        return cookies[-1]
    else:
        return cookies[rank]


leaves = get_leaves()