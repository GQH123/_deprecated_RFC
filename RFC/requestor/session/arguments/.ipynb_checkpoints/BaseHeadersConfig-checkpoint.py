from dataclasses import dataclass, field
from RFC.utils.functional_utils import BaseConfig


@dataclass
class BaseHeadersConfig(BaseConfig):
    headers_config: dict = field(default_factory={
        'base': {
            'method': 'switch',
            'params': {
                'base': 'default',
            },
        },
        'payload': {
            'method': 'passin',
            'params': {
                'ptype': dict
            },
        },
        'referer': {
            'method': 'from_url',
            'params': {
            },
        },
        'url': {
            'method': 'passin',
            'params': {
            },
        },
        'user-agent': {
            'method': 'random_fake',
            'params': {
                'type': 'firefox',
            },
        },
        'proxies': {
            'method': 'off',
            'params': {
            },
        },
        'kwargs': {
            'include': 'all',
            'exclude': None,
        },
    })