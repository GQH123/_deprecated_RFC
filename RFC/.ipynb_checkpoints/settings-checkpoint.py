import sys

setup_settings = {
    'requestor': {
    },
    'crawler': {
    },
    'kwargs': {
        'log_path': 'compile.log',
    },
}

init_settings = {
    'launcher': {
        'params': {
            'init': {
                'launch_name': 'example_name',
                'launch_time': 'current',
            },
            'launch': {
                'n_process': 8,
                'launch_method': 'spawn', # ['bash', 'spawn', 'forks']
            },
        },
        'logger': {
            'params': {
                'init': {
                    'root': './logs',
                    'subs': '{launch_time}_{launch_name}',
                    'types': {
                        'system': 'system.log',
                        'proxy_run': 'proxy_run_{rank}.log',
                        'proxy_history': 'proxy_history_{rank}.log',
                        'run': 'run_{rank}.log',
                        'error': 'error_{rank}.log',
                        'check': 'check_{rank}.log',
                    },
                },
                'log': {
                    'file': sys.stdout,
                    'note': '',
                    'mode': 'info',
                    'if_print': False,
                    'from_module': None,
                    'if_flush': True,
                },
            },
        },
        'divider': {
            'params': {
                'init': {
                    'workload_path': 'example_path',
                },
                'divide': {
                    'if_random': True,
                    'divide_method': 'even_number', #  ['even_number', 'even_size'(not always applicable)]
                },
            },
        },
    },
    'requestor': {
    },
    'kwargs': {
        'log_path': 'initialize.log',
    },
}

requestor_settings = {
}

controller_settings = {

}