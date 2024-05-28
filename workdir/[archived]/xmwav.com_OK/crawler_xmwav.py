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

# from proxy_pool import proxy_pool

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
        'url': ('field', 'https://www.xmwav.com/mscdetail/{id}.html'),
        # 'proxies': ('fixed', default_proxy_config),
        'proxies': ('qgnet', '31ZCGL9R', '2ED80C7D70D8'),
        # 'proxies': ('pool', tuple(proxy_pool)),
        'timeout': ('fixed', 20),
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
        'nproc': 3,
        'async_sema': 24,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 10,
        'request_sleep': 0,
    }
    
    @classmethod
    def _generate(cls, item, result):
        def parse_music_page(resp):
            parse_config = {
                'title': {
                    ('attr', 'div', 'class', 'info-bt', None): {
                        ('attr', 'h1', 'class', 'title', None): {
                            ('result', 'text', (('return_as_list', False),), None): {},
                        },
                        ('type', 'h2', 0): {
                            ('result', 'text', (('return_as_list', False),), None): {},
                        }
                    }
                },
                'metadata': {
                    ('attr', 'div', 'class', 'info-bt', None): {
                        ('type', 'small', 0): {
                            ('result', 'text', (('return_as_list', True),), None): {},
                        }
                    }
                },
                'tags': {
                    ('attr', 'div', 'class', 'info-bt', None): {
                        ('type', 'h5', 0): {
                            ('result', 'text', (('return_as_list', False),), None): {},
                        }
                    }
                },
                'links_title': {
                    ('attr', 'div', 'class', 'info-zi mb15', None): {
                        ('result', 'text', (('return_as_list', True),), None): {},
                    }
                },
                'links': {
                    ('attr', 'div', 'class', 'info-zi mb15', None): {
                        ('result', 'href', None): {},
                    }
                },
                'lyrics': {
                    ('attr', 'div', 'class', 'lrc', None): {
                        ('type', 'article', None): {
                            ('result', 'text', (('return_as_list', True),), None): {},
                        }
                    }
                },
            }
            title = parse(get_html_soup(resp.content), parse_config['title'])
            metadata = parse(get_html_soup(resp.content), parse_config['metadata'])
            tags = parse(get_html_soup(resp.content), parse_config['tags'])
            links_title = parse(get_html_soup(resp.content), parse_config['links_title'])
            links = parse(get_html_soup(resp.content), parse_config['links'])
            lyrics = parse(get_html_soup(resp.content), parse_config['lyrics'])
            return {
                'title': title,
                'metadata': metadata,
                'tags': tags,
                'links_title': links_title,
                'links': links,
                'lyrics': lyrics,
            }
        
        try:
            info = parse_music_page(result)
            # print(json.dumps(info, indent=4, ensure_ascii=False))
            json.dump(info, open(os.path.join(item.save_dir, f'{item.id}_info.json'), 'w'), indent=4, ensure_ascii=False)
        except Exception as e:
            error_report = f'[{type(e).__name__}] {str(e)}'
            cls._logger.error(f'Error when parsing music page {item.id}: {error_report}')
            print(f'Error when parsing music page {item.id}: {error_report}')
            pass


if __name__ == '__main__':
    auto_skipped_ids = []
    if os.path.exists('saved_logs/auto_skipped_ids.json'):
        auto_skipped_ids = json.load(open('saved_logs/auto_skipped_ids.json', 'r'))
    if os.path.exists('saved_logs/statistics_finished_status_details.json'):
        auto_skipped_ids += json.load(open('saved_logs/statistics_finished_status_details.json', 'r'))['__all__']['MusicPage']
    if os.path.exists('saved_logs/statistics_failed_status_details.json'):
        try:
            auto_skipped_ids += json.load(open('saved_logs/statistics_failed_status_details.json', 'r'))['StatusCode 500 Error']['type']['MusicPage']
        except Exception as e:
            pass
    auto_skipped_ids = list(set(auto_skipped_ids))
    print(f'number of auto_skipped_ids: {len(auto_skipped_ids)}')
    json.dump(auto_skipped_ids, open('saved_logs/auto_skipped_ids.json', 'w'), indent=4, ensure_ascii=False)


    # for x in auto_skipped_ids:
    #     try:
    #         x = int(x)
    #     except Exception as e:
    #         print(x)
    # exit(0)
    auto_skipped_ids = set([int(x) for x in auto_skipped_ids])

    from tqdm import tqdm
    id_bound = 150000
    # id_bound = 200
    added_ids = [id for id in tqdm(range(id_bound-1, 0-1, -1)) if id not in auto_skipped_ids]
    print(f'number of added_ids: {len(added_ids)}')
    MusicPage.start(ids=added_ids)
    pass