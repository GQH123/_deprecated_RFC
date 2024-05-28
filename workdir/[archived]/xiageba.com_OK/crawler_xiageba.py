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

proxy_pool = [
    {
        "http": "http://127.0.0.1:20000",
        "https": "http://127.0.0.1:20000",
        "all": "socks5://127.0.0.1:20000"
    },
    {
        "http": "http://127.0.0.1:20002",
        "https": "http://127.0.0.1:20002",
        "all": "socks5://127.0.0.1:20002"
    },
    {
        "http": "http://127.0.0.1:20004",
        "https": "http://127.0.0.1:20004",
        "all": "socks5://127.0.0.1:20004"
    },
    {
        "http": "http://127.0.0.1:20006",
        "https": "http://127.0.0.1:20006",
        "all": "socks5://127.0.0.1:20006"
    },
    {
        "http": "http://127.0.0.1:20008",
        "https": "http://127.0.0.1:20008",
        "all": "socks5://127.0.0.1:20008"
    },
    {
        "http": "http://127.0.0.1:20010",
        "https": "http://127.0.0.1:20010",
        "all": "socks5://127.0.0.1:20010"
    },
    {
        "http": "http://127.0.0.1:20012",
        "https": "http://127.0.0.1:20012",
        "all": "socks5://127.0.0.1:20012"
    },
    {
        "http": "http://127.0.0.1:20014",
        "https": "http://127.0.0.1:20014",
        "all": "socks5://127.0.0.1:20014"
    },
    {
        "http": "http://127.0.0.1:20016",
        "https": "http://127.0.0.1:20016",
        "all": "socks5://127.0.0.1:20016"
    },
    {
        "http": "http://127.0.0.1:20018",
        "https": "http://127.0.0.1:20018",
        "all": "socks5://127.0.0.1:20018"
    },
    {
        "http": "http://127.0.0.1:20020",
        "https": "http://127.0.0.1:20020",
        "all": "socks5://127.0.0.1:20020"
    },
    {
        "http": "http://127.0.0.1:20022",
        "https": "http://127.0.0.1:20022",
        "all": "socks5://127.0.0.1:20022"
    },
    {
        "http": "http://127.0.0.1:20024",
        "https": "http://127.0.0.1:20024",
        "all": "socks5://127.0.0.1:20024"
    },
    {
        "http": "http://127.0.0.1:20026",
        "https": "http://127.0.0.1:20026",
        "all": "socks5://127.0.0.1:20026"
    },
    {
        "http": "http://127.0.0.1:20028",
        "https": "http://127.0.0.1:20028",
        "all": "socks5://127.0.0.1:20028"
    },
    {
        "http": "http://127.0.0.1:20030",
        "https": "http://127.0.0.1:20030",
        "all": "socks5://127.0.0.1:20030"
    },
    {
        "http": "http://127.0.0.1:20032",
        "https": "http://127.0.0.1:20032",
        "all": "socks5://127.0.0.1:20032"
    },
    {
        "http": "http://127.0.0.1:20034",
        "https": "http://127.0.0.1:20034",
        "all": "socks5://127.0.0.1:20034"
    },
    {
        "http": "http://127.0.0.1:20036",
        "https": "http://127.0.0.1:20036",
        "all": "socks5://127.0.0.1:20036"
    },
    {
        "http": "http://127.0.0.1:20038",
        "https": "http://127.0.0.1:20038",
        "all": "socks5://127.0.0.1:20038"
    },
    {
        "http": "http://127.0.0.1:20040",
        "https": "http://127.0.0.1:20040",
        "all": "socks5://127.0.0.1:20040"
    },
    {
        "http": "http://127.0.0.1:20042",
        "https": "http://127.0.0.1:20042",
        "all": "socks5://127.0.0.1:20042"
    },
    {
        "http": "http://127.0.0.1:20044",
        "https": "http://127.0.0.1:20044",
        "all": "socks5://127.0.0.1:20044"
    },
    {
        "http": "http://127.0.0.1:20046",
        "https": "http://127.0.0.1:20046",
        "all": "socks5://127.0.0.1:20046"
    }
]


class MusicPage(ItemType):
    _name: str = 'music_page'

    _logger = None
    request_arg_group = {
        'url': ('field', 'https://xiageba.com/music/{id}'),
        # 'proxies': ('fixed', default_proxy_config),
        # 'proxies': ('qgnet', 'D6FL1CJ8', '9FC1ADB88090'),
        'proxies': ('pool', tuple(proxy_pool)),
    }
    item_arg_group = {
        'save_dir': ('auto', 'saves', 'subs'),
    }
    session_args = {
        'no_session': False,
        'lib': 'requests',
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
        'nproc': 24,
        'async_sema': 1,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 10,
        'request_sleep': 0.3,
        
        # 24, 0.5, 1000 -> 0m31.107s, 129
        # 24, 0.4, 1000 -> 0m31.107s, 129
        # 24, 0.3, 1000 -> 0m31.107s, 129
        # 24, 0.2, 1000 -> 0m21.809s, 308
        # 24, 0.1, 1000 -> 0m21.115s, 400
        
        # 24, 0.3, 100  -> 0m17.955s, 3
        
        # 1, 0.5, 100   -> 1m21.852s, 2
        # 1, 0.3, 100   -> 1m11.329s, 3
        # 1, 0.2, 100   -> 1m1.131s, 20
        # 1, 0.1, 100   -> 1m1.089s, 43
    }
    
    @classmethod
    def _generate(cls, item, result):
        def parse_music_info(resp):
            parse_config = {
                'metas': {
                    ('attr', 'div', 'class', 'd-flex flex-column justify-content-center', None): {
                        ('type', 'div', None): {
                            ('result', 'text', (('return_as_list', True),), None): {},
                        }
                    }
                },
                'links': {
                    ('attr', 'div', 'class', 'down-item', None): {
                        ('result', 'text', (('return_as_list', True),), None): {},
                    }
                },
                'tags': {
                    ('attr', 'div', 'class', 'd-flex flex-wrap', 0): {
                        ('type', 'a', None): {
                            ('result', 'text', (('return_as_list', True),), None): {},
                        }
                    }
                },
                'lyrics': {
                    ('attr', 'div', 'class', 'border-top mt-3 pt-3', None): {
                        ('attr', 'div', 'class', 'mt-2', 0): {
                            ('result', 'text', (('sep', '\n'), ('return_as_list', True),), None): {},
                        }
                    }
                }
                
            }
            links = parse(get_html_soup(resp.content), parse_config['links'])
            _links = []
            for link in links:
                if len(link) & 1:
                    link.append('')
                for i, part in enumerate(link[::2]):
                    if part.endswith(':'):
                        link[i*2] = part[:-1]
                _links.append({k: v for k, v in zip(link[::2], link[1::2])})
            metas = parse(get_html_soup(resp.content), parse_config['metas'])
            tags = parse(get_html_soup(resp.content), parse_config['tags'])
            lyrics = parse(get_html_soup(resp.content), parse_config['lyrics'], debug=False)
            # we delay the format checking to the post-processing stage
            return {
                'metadata': metas,
                'tags': tags,
                'links': _links,
                'lyrics': lyrics,
            }

        info = parse_music_info(result)
        json.dump(info, open(os.path.join(item.save_dir, f'{item.id}_info.json'), 'w'), indent=4, ensure_ascii=False)


if __name__ == '__main__':
    # MusicPage.start(ids=range(120000))
    ids = json.load(open('saved_logs/statistics_failed_exceptions_details.json', 'r'))['__all__']
    MusicPage.start(ids=ids)