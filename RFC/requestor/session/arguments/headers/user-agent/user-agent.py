from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import ParamValueError
from fake_useragent import UserAgent
ua = UserAgent()


@leaf()
def init(**kwargs):
    ...


@leaf(freeze=True)
def fixed(value, **kwargs):
    return value


@leaf()
def random_fake(type, **kwargs):
    if type not in ua.browsers + ['random']:
        raise ParamValueError('type', type, ua.browsers + ['random'], __name__)
    return ua[type]


@leaf(freeze=True)
def none(**kwargs):
    return ''


leaves = get_leaves()