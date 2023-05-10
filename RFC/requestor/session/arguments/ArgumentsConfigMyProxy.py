from dataclasses import dataclass, field, InitVar
from .ArgumentsConfig import ArgumentsConfig


options = {
    'default': {
        'method': 'login',
        'kwargs': {
            'type': 'QGNet',
            'username': 'D6FL1CJ8',
            'password': '9FC1ADB88090',
        },
    }
}


@dataclass
class ArgumentsConfigMyProxy(ArgumentsConfig):
    hist_log: InitVar[str | None] = None
    run_log: InitVar[str | None] = None
    proxy_type: InitVar[str] = 'default'
    rank: InitVar[int] = 0
                      
    def __post_init__(
            self, 
            hist_log,
            run_log,
            proxy_type,
            rank,
        ):
        super().__post_init__()
        if hist_log is None:
            hist_log = f'proxy_history_{rank}.log'
        if run_log is None:
            run_log = f'proxy_run_{rank}.log'
        proxy_settings = options[proxy_type].copy()
        proxy_settings['kwargs'].update(dict(
            hist_log=hist_log,
            run_log=run_log,
            rank=rank,
        ))
        self.config['proxies'] = proxy_settings
    
    def __call__(self, hist_log=None, run_log=None, proxy_type='default', rank=0, **kwargs):
        super().__call__(**kwargs)
        self.__post_init__(hist_log, run_log, proxy_type, rank)
        return self