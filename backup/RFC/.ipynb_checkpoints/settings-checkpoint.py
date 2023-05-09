static_header = {
    'connection': 'keep-alive',
    'upgrade-insecure-requests': '1',
    'sec-fetch-dest': 'document',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'navigate',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7,en-GB;q=0.6,ru;q=0.5',
}

settings = {
    'global': {
        'run_log': 'run_log_%(rank)d.txt',
        'error_log': 'error_log_%(rank)d.txt',
        'proxy_run_log': 'proxy_run_log_%(rank)d.txt',
        'proxy_hist_log': 'proxy_hist_log_%(rank)d.txt',
        'parser_log': 'parser_log_%(rank)d.txt',
        'rank': 0,
    },
    'network_layer': {
        'headers': {
            'user-agent': {
                'firefox': {},
                'random': {},
                'none': {},
                'fixed': {
                    'value': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
                },
                'kwargs': {
                    'default_method': 'firefox',
                    'freeze': 'auto',
                    'include': 'all',
                    'exclude': None,
                },
            },
            'referer': {
                'from_url_once': {},
                'fixed': {
                    'value': 'www.example.com',
                },
                'none': {},
                'kwargs': {
                    'default_method': 'from_url_once',
                    'freeze': 'auto',
                    'include': 'all',
                    'exclude': None,
                },
            },
            'kwargs': {
                'static_header': {
                    'use': True,
                    'force': False,
                    'value': static_header,
                },
                'include': 'all',
                'exclude': None,
            },
        },
        'cookies': {
            'from_file_once': {
                'file_path': 'cookies.txt',
                'format': 'dict',
                'format_args': {},
            },
            'from_file': {
                'file_path': 'cookies.txt',
                'format': 'dict',
                'format_args': {},
            },
            'fixed': {
                'value': 'key1=value1',
                'format': 'dict',
                'format_args': {},
            },
            'kwargs': {
                'default_method': 'fixed',
                'freeze': 'auto',
                'include': 'all',
                'exclude': None,
            },
        },
        'proxies': {
            'from_manager': {},
            'fixed': {
                'server_addr': '127.0.0.1:7890',
            },
            'none': {},
            'login': {},
            'kwargs': {
                'default_method': 'login',
                'freeze': 'auto',
                'manager': {
                    'launch_mode': 'inprocess',  # ['inprocess', 'outprocess', 'off']
                    'server_addr': '',
                    'username': '',
                    'password': '',
                },
                'include': 'all',
                'exclude': None,
            },
        },
        'kwargs': {
            'include': 'all',
            'exclude': None,
            'debug': True,
        },
    },
    'middleware_layer': {
    },
    'crawler_layer': {
    },
    'parser_layer': {
        'soup': 'from_html',
        'apply_key': {
            'getstr': True,
            'debug': False,
            'proc': lambda s: s,
        },
    },
}