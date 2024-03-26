import re
import json
import time
import requests

from RFC.item.item import ItemType


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


class PaperWeeklyZhihuArticlePage(ItemType):
    """
        Zhihu APIv4 will bonus you with article contents (in html)
    """
    _name: str = 'paperweekly_zhihu_article_page'

    _logger = None
    request_arg_group = {
        'url': ('field', '{url}'),
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
        'json_saver': {},
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
        data = result['json']
        is_end = data['paging']['is_end']
        if is_end:
            return
        next_url = data['paging']['next']
        offset = re.search(r'offset=(\d+)', next_url).group(1)
        assert int(offset) % 100 == 0, f'offset {offset} not divisible by 100'
        PaperWeeklyZhihuArticlePage._add_items(ids=int(offset)//100, url=next_url, bloodline=item.bloodline[:-1])


PaperWeeklyZhihuArticlePage.start(ids=0, url='https://www.zhihu.com/api/v4/columns/paperweekly/items?limit=100&offset=0')