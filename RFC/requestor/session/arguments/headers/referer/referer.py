from RFC.utils.structural_utils import leaf, get_leaves
from urllib.parse import urlparse


@leaf()
def init(**kwargs):
    ...



@leaf(freeze=True)
def from_url_once(url, **kwargs):
    return '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))


@leaf()
def from_url(url, **kwargs):
    return '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))


@leaf(freeze=True)
def fixed(value, **kwargs):
    return value


@leaf(freeze=True)
def none(**kwargs):
    return ''


leaves = get_leaves()