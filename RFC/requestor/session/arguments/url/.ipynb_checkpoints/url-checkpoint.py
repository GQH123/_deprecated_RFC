from RFC.utils.structural_utils import leaf, get_leaves


@leaf()
def init(**kwargs):
    ...


@leaf()
def passin(url, **kwargs):
    return url


leaves = get_leaves()