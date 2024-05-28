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


class MyItemType(ItemType):
    _name: str = 'my_itemtype'

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


if __name__ == '__main__':
    auto_skipped_ids = {}
    if os.path.exists('saved_logs/auto_skipped_ids.json'):
        auto_skipped_ids = json.load(open('saved_logs/auto_skipped_ids.json', 'r'))
    if os.path.exists('saved_logs/statistics_finished_status_details.json'):
        parsed_skipped_ids = json.load(open('saved_logs/statistics_finished_status_details.json', 'r'))['__all__']['MyItemType']
        for item_type in parsed_skipped_ids:
            auto_skipped_ids[item_type] = list(set(auto_skipped_ids.get(item_type, []) + parsed_skipped_ids[item_type]))
    auto_skipped_ids_count = {item_type: len(auto_skipped_ids[item_type]) for item_type in auto_skipped_ids}
    print(f'count for auto_skipped_ids:\n{json.dumps(auto_skipped_ids_count, indent=4, ensure_ascii=False)}')
    json.dump(auto_skipped_ids, open('saved_logs/auto_skipped_ids.json', 'w'), indent=4, ensure_ascii=False)
    auto_skipped_ids = {item_type: set(auto_skipped_ids[item_type]) for item_type in auto_skipped_ids}

    """ example for filtering ids
    ids = [f'{type}_{tag}' for type in type_tag_dict for tag in type_tag_dict[type]]
    items_kwargs = [{'paper_type': type, 'paper_tag': tag, 'symbol': '?' if type == 'venue' else '&'} for type in type_tag_dict for tag in type_tag_dict[type]]
    print(f'count for all ids: {len(ids)}\n')
    ids_items_kwargs = [(id, item_kwargs) for id, item_kwargs in zip(ids, items_kwargs) if id not in auto_skipped_ids.get('PapersCoolPaperPage', set())]
    if ids_items_kwargs:
        ids, items_kwargs = zip(*ids_items_kwargs)
    else:
        ids, items_kwargs = [], []
    print(f'count for added ids: {len(ids)}\n')
    """

    # make sure item id contains no '/' so that item.save_dir will be a valid path, and better use unique id for each item (but not necessary) for convenience
    
    # MyItemType.start(ids=ids, items_kwargs=items_kwargs, bloodline=[])
    ...