import re
import os
import json
import time
import requests

from RFC.item.item import ItemType
from RFC.utils.parse import (
    get_html_soup,
    parse,
)


default_proxy_config = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
    'all': 'socks5://127.0.0.1:7890',
}


# default_proxy_config = {
#     'http': 'http://10.176.52.116:7890',
#     'https': 'http://10.176.52.116:7890',
#     'all': 'socks5://10.176.52.116:7890',
# }


class ItemTypeName(ItemType):
    _name: str = 'itemtype_name'

    _logger = None
    request_arg_group = {
        'url': ('field', '<url>'),
        'proxies': ('fixed', default_proxy_config),
    }
    item_arg_group = {
        'save_dir': ('auto', 'saves', 'subs'),
    }
    session_args = {
        'no_session': False,
        'lib': 'aiohttp',
    }
    middleware_args = {
        'status_code': {
            'expected_status_codes': [200],
        },
        'basic': {},
        'content_saver': {},
        'result_saver': {},
    }
    requestor_args = {
        'nproc': 1,
        'async_sema': 24,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 10,
    }
    
    @classmethod
    def _generate(cls, item, result):
        ...