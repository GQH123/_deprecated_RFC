from dataclasses import dataclass, field
from .BaseHeadersConfig import BaseHeadersConfig


options = {
    'default': {
        'method': 'login',
        'params': {
            'type': 'QGNet',
            'username': 'D6FL1CJ8',
            'password': '9FC1ADB88090',
        },
    }
}


@dataclass
class MyProxyHeadersConfig(BaseHeadersConfig):
    def __init__(self, hist_log, run_log, proxy_type='default', rank=-1):
        options[proxy_type].update(dict(
            hist_log=hist_log,
            run_log=run_log,
            rank=rank,
        ))
        self.headers_config['proxies'] = options[proxy_type]