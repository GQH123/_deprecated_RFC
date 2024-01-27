import os

from .env import ENV
from .types import *


def get_config(project_path):
    project_name = os.path.basename(project_path)

    config = {
        'docs': {
            'refs': {}
        },
        'saves': {},
        'logs': {},
        'crawler.py': cp('crawler_template.py'),
    }

    return config