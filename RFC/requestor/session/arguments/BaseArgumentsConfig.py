from dataclasses import dataclass, field
from RFC.utils.BaseConfig import BaseConfig


options = {
    'default': {
        'headers': {
            'base': {
                'method': 'switch',
                'kwargs': {
                    'option': 'default',
                },
            },
            'user-agent': {
                'method': 'random_fake',
                'kwargs': {
                    'type': 'firefox',
                },
            },
            'referer': {
                'method': 'from_url',
                'kwargs': {
                },
            },
            'kwargs': {
            },
        },
        'url': {
            'method': 'passin',
            'kwargs': {
            },
        },
        'payload': {
            'method': 'passin',
            'kwargs': {
                'ptype': dict,
            },
        },
        'params': {
            'method': 'passin',
            'kwargs': {
                'ptype': dict,
            },
        },
        'proxies': {
            'method': 'off',
            'kwargs': {
            },
        },
        'cookies': {
            'method': 'passin',
            'kwargs': {
                'ctype': dict,
            },
        },
        'kwargs': {
        },
    },
}


def get_option(name='default'):
    return options[name].copy()


"""
class BaseArgumentsConfig(dict, BaseConfig):
    def __init__(
        self,
        option: str = 'default',
    ):

        super().__init__(get_option(option))
        super(dict, self).__init__()
"""


@dataclass
class BaseArgumentsConfig(BaseConfig):
    config: dict = field(default_factory=get_option)

    def __call__(
        self,
        **kwargs,
    ):
        config = kwargs.pop('config', {})
        self.__dict__.update(kwargs)
        self.__dict__['config'].update(config)
        return self