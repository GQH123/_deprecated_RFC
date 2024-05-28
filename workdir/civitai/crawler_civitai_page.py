import os
import json
import time
import requests

from RFC.item.item import ItemType
from RFC.utils.parse import (
    parse,
    get_html_soup
)
from RFC.utils.func import save_object


# default_proxy_config = {
#     'http': 'http://127.0.0.1:7890',
#     'https': 'http://127.0.0.1:7890',
#     'all': 'socks5://127.0.0.1:7890',
# }


default_proxy_config = {
    'http': 'http://10.176.52.116:7890',
    'https': 'http://10.176.52.116:7890',
    'all': 'socks5://10.176.52.116:7890',
}


class CivitaiModelPage(ItemType):
    _name: str = 'itemtype_civitai_model_page'

    _logger = None
    request_arg_group = {
        'url': ('field', 'https://civitai.com/models/{id}'),
        'proxies': ('fixed', default_proxy_config),
        'headers': ('fixed', {}),
    }
    item_arg_group = {
        'save_dir': ('auto', 'saves/json/', 'subs'),
    }
    session_args = {
        'no_session': False,
        'lib': 'aiohttp',
    }
    middleware_args = {
        'status_code': {
            'expected_status_codes': [200, 404],
        },
        'basic': {},
        'text_saver': {},
        'result_saver': {},
    }
    requestor_args = {
        'nproc': 12,
        'async_sema': 24,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 10,
    }
    
    @classmethod
    def _generate(cls, item, result):
        parse_config = {
            ('attr', 'script', 'id', '__NEXT_DATA__', -1): {
                ('result', 'text', None): {}
            }
        }
        parsed_json = json.loads(parse(get_html_soup(result.text), parse_config, return_str=True, debug=True)[0])
        save_object(parsed_json, os.path.join(item.save_dir, f'{item.id}.json'), 'json', None)
        try:
            parsed_model_json = parsed_json['props']['pageProps']['trpcState']['json']['queries'][-1]['state']
        except Exception:
            parsed_model_json = {}
        save_object(parsed_model_json, os.path.join(item.save_dir, 'model.json'), 'json', None)
        pass


def load_all_failed():
    failed_ids = []
    data = json.load(open('saved_logs/statistics_failed_exceptions_details.json'))
    for error in data:
        failed_ids += data[error]['type']['CivitaiModelPage']
    return failed_ids


# CivitaiModelPage.start(range(300000))
# CivitaiModelPage.start(181865)
# CivitaiModelPage.start(range(401000))
# CivitaiModelPage.start(range(300000, 401000))
# CivitaiModelPage.start(load_all_failed())
