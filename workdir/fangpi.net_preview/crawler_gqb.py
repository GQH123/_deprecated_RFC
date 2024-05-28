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

from proxy_pool import proxy_pool

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


class MusicPreview(ItemType):
    _name: str = 'music_preview'

    _logger = None
    request_arg_group = {
        'url': ('field', 'https://www.fangpi.net/api/play_url?id={id}'),
        # 'proxies': ('fixed', default_proxy_config),
        'proxies': ('qgnet', '31ZCGL9R', '2ED80C7D70D8'),
        # 'proxies': ('zmhttp', 'http://webapi.http.zhimacangku.com/getip?neek=321a408a&num=1&type=2&pro=210000&city=0&yys=0&port=1&pack=344217&ts=1&ys=1&cs=1&lb=1&sb=&pb=4&mr=3&regions='),
        # 'proxies': ('pool', tuple(proxy_pool)),
        # 'timeout': ('fixed', 120),
        'timeout': ('fixed', 60),
    }
    item_arg_group = {
        'save_dir': ('auto', 'saves', 'subs'),
    }
    session_args = {
        'no_session': False,
        'lib': 'aiohttp',
        'timeout': 60,  # remember to set timeout when using proxy api
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
        'nproc': 12,  # 24
        'async_sema': 6,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 10,
        'request_sleep': 0,
    }
    
    @classmethod
    def _generate(cls, item, result):
        pass

  
auto_skipped_ids = {}
if os.path.exists('saved_logs/auto_skipped_ids.json'):
    auto_skipped_ids = json.load(open('saved_logs/auto_skipped_ids.json', 'r'))
if os.path.exists('saved_logs/statistics_finished_status_details.json'):
    parsed_skipped_ids = json.load(open('saved_logs/statistics_finished_status_details.json', 'r'))['__all__']
    for item_type in parsed_skipped_ids:
        auto_skipped_ids[item_type] = list(set(auto_skipped_ids.get(item_type, []) + parsed_skipped_ids[item_type]))
auto_skipped_ids_count = {item_type: len(auto_skipped_ids[item_type]) for item_type in auto_skipped_ids}
print(f'count for auto_skipped_ids:\n{json.dumps(auto_skipped_ids_count, indent=4, ensure_ascii=False)}')
json.dump(auto_skipped_ids, open('saved_logs/auto_skipped_ids.json', 'w'), indent=4, ensure_ascii=False)
auto_skipped_ids = {item_type: set(auto_skipped_ids[item_type]) for item_type in auto_skipped_ids}

ids = range(13600000-1, 0-1, -1)
print(f'number of all ids: {len(ids)}')
ids = [id for id in ids if str(id) not in auto_skipped_ids['MusicPreview']]
print(f'number of added ids: {len(ids)}')

if __name__ == '__main__':
    # MusicPreview.start(ids=range(1000))
    MusicPreview.start(ids=ids)
    pass

# 13260000, but their update is very fast, so this id upper bound will be surpassed soon