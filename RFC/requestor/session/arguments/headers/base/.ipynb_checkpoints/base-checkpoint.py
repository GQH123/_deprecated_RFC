from RFC.utils.structural_utils import leaf, get_leaves


options = {
    'default': {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7,en-GB;q=0.6,ru;q=0.5',
    },
}


@leaf()
def init(**kwargs):
    ...


@leaf(freeze=True)
def fixed(base, **kwargs):
    return base


@leaf()
def passin(base, **kwargs):
    return base


@leaf()
def switch(base, **kwargs):
    return options[base]


leaves = get_leaves()