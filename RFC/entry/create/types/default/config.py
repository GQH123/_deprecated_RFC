import os

from .env import ENV
from .types import *


def get_config(project_path):
    project_name = os.path.basename(project_path)

    config = {
        'dist_clash': cpdir('dist_clash'),
        'docs': {'refs': {}},
        'saves': {},
        'saved_logs': {},
        'logs': {},
        'examples': {
            'crawler_example.py': cp('crawler_example.py'),
            'debug_example.ipynb': cp('debug_example.ipynb'),
        },
        'crawler_xxx.py': cp('crawler.py'),
        'debug.ipynb': cp('debug.ipynb'),
        'run_nohup.sh': cp('run_nohup.sh'),
        'extract.py': cp('extract.py'),
        'csaves.py': cp('compress_saves.py'),
        'dsaves.py': cp('decompress_saves.py'),
        'killall.sh': cp('killall.sh'),
        'monitor.py': cp('monitor.py'),
    }

    return config