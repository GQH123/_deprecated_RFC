import os
import re
import json
import time
import requests

from RFC.item.item import ItemType
from RFC.utils.parse import (
    get_html_soup,
    parse,
)


default_proxy_config = {
    'http': 'http://10.176.52.116:7890',
    'https': 'http://10.176.52.116:7890',
    'all': 'socks5://10.176.52.116:7890',
}


global_news_count = 0


class FudanNewsList(ItemType):
    _name: str = 'fudan_news_list'

    _logger = None
    request_arg_group = {
        'url': ('field', 'https://news.fudan.edu.cn/pbl/list{id}.psp'),
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
        'text_saver': {},
        'content_saver': {},
        'result_saver': {},
    }
    requestor_args = {
        'nproc': 1,
        'async_sema': 24,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 1,
    }
    
    @classmethod
    def _generate(cls, item, result):
        host = 'https://news.fudan.edu.cn'
        parse_config = {
            ('attr', 'div', 'class', 'news_text', None): {
                ('type', 'a', None): {},
            },
        }
        # print(result.text)
        links = parse(get_html_soup(result.text), parse_config, return_str=False, debug=False)
        for link in links:
            url = host + link['href']
            id = url.split('/')[-2]
            FudanNews._add_items(ids=id, url=url, bloodline=item.bloodline)
            
            
class FudanNews(FudanNewsList):
    _name: str = 'fudan_news'

    _logger = None
    request_arg_group = {
        'url': ('field', '{url}'),
        'proxies': ('fixed', default_proxy_config),
    }
    
    @classmethod
    def _generate(cls, item, result):
        parse_config = {
            'body': {
                ('attr', 'div', 'class', 'wp_articlecontent', None): {
                    ('result', 'text', None): {},
                },
            },
            'category': {
                ('attr', 'span', 'class', 'artCat_v1', None): {
                    ('result', 'text', None): {},
                },
            },
            'title': {
                ('attr', 'h1', 'class', 'arti_title', None): {
                    ('result', 'text', None): {},
                },
            },
            'metas': {
                ('attr', 'p', 'class', 'arti_metas', 0): {
                    ('type', 'span', None): {},
                },
            },
        }
        _result = result
        soup = get_html_soup(_result.text)
        result = {}
        result['title'] = parse(soup, parse_config['title'], return_str=True, debug=False)
        if result['title']:
            result['title'] = result['title'][0]
        else:
            result['title'] = ''
        result['category'] = parse(soup, parse_config['category'], return_str=True, debug=False)
        if result['category']:
            result['category'] = result['category'][0]
        else:
            result['category'] = ''
        result['metas'] = {}
        metas = parse(soup, parse_config['metas'], return_str=False, debug=False)
        for meta in metas:
            meta = meta.text
            if '：' not in meta:
                continue
            k, v = meta.split('：', 1)
            result['metas'][k] = v
        result['body'] = parse(soup, parse_config['body'], return_str=True, debug=False)
        if result['body']:
            result['body'] = result['body'][0]
        else:
            result['body'] = ''
        json.dump(result, open(os.path.join(item.save_dir, 'news.json'), 'w'), indent=4, ensure_ascii=False)


ids = list(range(1, 121))
FudanNewsList.start(ids)