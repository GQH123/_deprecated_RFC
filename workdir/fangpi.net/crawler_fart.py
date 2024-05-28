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


class MusicPage(ItemType):
    _name: str = 'music_page'

    _logger = None
    request_arg_group = {
        'url': ('field', 'https://www.fangpi.net/music/{id}'),
        # 'proxies': ('fixed', default_proxy_config),
        # 'proxies': ('qgnet', '31ZCGL9R', '2ED80C7D70D8'),
        'proxies': ('pool', tuple(proxy_pool)),
        'timeout': ('fixed', 60),
    }
    item_arg_group = {
        'save_dir': ('auto', 'saves', 'subs'),
    }
    session_args = {
        'no_session': False,
        'lib': 'aiohttp',
        # 'timeout': 60,  # remember to set timeout when using proxy api
    }
    middleware_args = {
        'status_code': {
            'expected_status_codes': [200],
        },
        'basic': {},
        'content_saver': {},
        'text_saver': {},
        'result_saver': {},
    }
    requestor_args = {
        'nproc': 174,
        'async_sema': 3,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 10,
        'request_sleep': 0,
    }
    
    @classmethod
    def _generate(cls, item, result):
    
        # def parse_music_info(resp):
        #     parse_config = {
        #         'title': {
        #             ('attr', 'span', 'class', 'badge badge-pill badge-info', None): {
        #                 ('result', 'text', (('return_as_list', True),), None): {},
        #             }
        #         },
        #     }
        #     title = parse(get_html_soup(resp.content), parse_config['title'])
        #     # we delay the format checking to the post-processing stage
        #     results = {
        #         'title': title,
        #     }
        #     return results
    
        def parse_music_page_re(resp):
            info = {k: v for k, v in re.findall('window.([0-9a-z_]*) = (.*);', resp.text)}
            info['mp3_lrc'] = [part for part in '\n'.join(re.findall('window.mp3_lrc = `((?:.*)(?:\n.*)*)`;', resp.text, re.MULTILINE)).split('\n') if part]
            if len(info) == 1 and not info['mp3_lrc']:
                info = {}
            return info
        try:
            info = parse_music_page_re(result)
            if info:
                json.dump(info, open(os.path.join(item.save_dir, f'{item.id}_info.json'), 'w'), indent=4, ensure_ascii=False)
        except Exception as e:
            error_report = f'[{type(e).__name__}] {str(e)}'
            cls._logger.error(f'Error when parsing music page {item.id}: {error_report}')
            print(f'Error when parsing music page {item.id}: {error_report}')
            pass
        

auto_skipped_ids = []
if os.path.exists('saved_logs/auto_skipped_ids.json'):
    auto_skipped_ids = json.load(open('saved_logs/auto_skipped_ids.json', 'r'))
if os.path.exists('saved_logs/statistics_finished_status_details.json'):
    auto_skipped_ids += json.load(open('saved_logs/statistics_finished_status_details.json', 'r'))['__all__']
auto_skipped_ids = list(set(auto_skipped_ids))
print(f'number of auto_skipped_ids: {len(auto_skipped_ids)}')
json.dump(auto_skipped_ids, open('saved_logs/auto_skipped_ids.json', 'w'), indent=4, ensure_ascii=False)
auto_skipped_ids = set([int(x) for x in auto_skipped_ids])

if __name__ == '__main__':
    from tqdm import tqdm
    added_ids = [id for id in tqdm(range(13600000-1, 0-1, -1)) if id not in auto_skipped_ids]
    print(f'number of added_ids: {len(added_ids)}')
    # MusicPage.start(ids=range(10))
    MusicPage.start(ids=added_ids)
    # 13600000, but their update is very fast, so this id upper bound will be surpassed soon
    # 13260000
    pass