import os

from .env import ENV
from .types import *


def get_config(project_path):
    project_name = os.path.basename(project_path)

    config = {
        'docs': {'refs': {}},
        'saves': {},
        'logs': {},
        'examples': {},
        'crawler_example.py': cp('crawler_example.py'),
        'debug_example.ipynb': cp('debug_example.ipynb'),
    }

    return config