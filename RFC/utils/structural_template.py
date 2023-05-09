from RFC.utils.structural_utils import leaf, get_leaves


@leaf()
def init(**kwargs):
    pass


@leaf()
def func1(**kwargs):
    pass


@leaf()
async def func2(**kwargs):
    pass


leaves = get_leaves()