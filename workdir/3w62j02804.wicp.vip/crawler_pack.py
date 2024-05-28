import re
import os
import json
import time
import requests
# import hashlib

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

default_cookies = {
    'auth': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjp7ImlkIjo0NDUxLCJsb2NhbGUiOiJ6aC1jbiIsInZpZXdNb2RlIjoibGlzdCIsInNpbmdsZUNsaWNrIjpmYWxzZSwicGVybSI6eyJhZG1pbiI6ZmFsc2UsImV4ZWN1dGUiOmZhbHNlLCJjcmVhdGUiOmZhbHNlLCJyZW5hbWUiOmZhbHNlLCJtb2RpZnkiOmZhbHNlLCJkZWxldGUiOmZhbHNlLCJzaGFyZSI6ZmFsc2UsImRvd25sb2FkIjp0cnVlfSwiY29tbWFuZHMiOltdLCJsb2NrUGFzc3dvcmQiOmZhbHNlLCJoaWRlRG90ZmlsZXMiOmZhbHNlLCJkYXRlRm9ybWF0IjpmYWxzZX0sImlzcyI6IkZpbGUgQnJvd3NlciIsImV4cCI6MTc1MjcyMjgyMywiaWF0IjoxNzE2NzIyODIzfQ.WPvI80RFSsQGEEb24lJwI51ZM7e7gHQwQOZKHNVXQns'
}

default_headers = {
    'host': '3w62j02804.wicp.vip:66',
    'x-auth': default_cookies['auth'],
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

default_cookies_json = json.dumps(default_cookies)
default_headers_json = json.dumps(default_headers)


def renew_cookies(headers, cookies, skipped=False):
    try:
        if skipped:
            return json.dumps(headers), json.dumps(cookies)
        retry_limit = 5
        for i in range(retry_limit):
            try:
                resp = requests.post('http://3w62j02804.wicp.vip:66/api/renew', proxies=default_proxy_config, headers=headers, cookies=cookies, timeout=10).text
                assert resp, 'client cookies request error: empty response'
                cookies = json.dumps({'auth': resp})
                headers = json.dumps({'host': '3w62j02804.wicp.vip:66', 'x-auth': resp, 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'})
                return headers, cookies
            except Exception as e:
                error_report = f'cookies request error: [{type(e).__name__}] {e}'
                print(error_report, flush=True)
                time.sleep(2)
                if i == retry_limit-1:
                    raise e
                pass
    except Exception as e:
        error_report = f'cookies request error: [{type(e).__name__}] {e}'
        print(error_report, flush=True)
        return json.dumps(headers), json.dumps(cookies)


class PackDirStructure(ItemType):
    _name: str = 'pack_dir_structure'

    _logger = None
    request_arg_group = {
        'url': ('field', 'http://3w62j02804.wicp.vip:66/api/resources/{path}'),
        'proxies': ('fixed', default_proxy_config),
        'cookies': ('field_json', '{cookies_json}'),
        'retry_limit': ('fixed', 3),
        'headers': ('field_json', '{headers_json}'),
        'timeout': ('fixed', 5),
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
        'nproc': 6,
        'async_sema': 1,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 1,
    }
    
    @classmethod
    def _generate(cls, item, result):
        dir_info = result.content.decode('utf-8')
        dir_info = json.loads(dir_info)
        json.dump(dir_info, open(os.path.join(item.save_dir, 'dir_info.json'), 'w'), indent=4, ensure_ascii=False)
        ids = []
        items_kwargs = []
        file_ids = []
        file_items_kwargs = []
        my_path = item.path
        for part in dir_info['items']:
            part_id = part['name']
            # part_path = os.path.join(my_path, part['path'])
            part_path = part['path']
            if part_path.startswith('/'):
                part_path = part_path[1:]
            if '#' in part_path:
                part_path = part_path.replace('#', '%23')
            if not part['isDir']:
                file_ids.append(part_id)
                # skipped = os.path.exists(os.path.join(item.save_dir, 'subs', part_id, '_result.pkl'))
                skipped = True
                headers_json, cookies_json = renew_cookies(item.headers, item.cookies, skipped=skipped)
                file_items_kwargs.append({'path': part_path, 'cookies_json': cookies_json, 'headers_json': headers_json})
                continue
            # path_md5 = hashlib.md5(part_path.encode('utf-8')).hexdigest()[:12]
            # print(item.headers, item.cookies)
            ids.append(part_id)
            # skipped = os.path.exists(os.path.join(item.save_dir, 'subs', part_id, 'dir_info.json'))
            skipped = True
            headers_json, cookies_json = renew_cookies(item.headers, item.cookies, skipped=skipped)
            items_kwargs.append({'path': part_path, 'cookies_json': cookies_json, 'headers_json': headers_json})
        PackDirStructure._add_items(ids=ids, items_kwargs=items_kwargs, bloodline=item.bloodline)
        PackFile._add_items(ids=file_ids, items_kwargs=file_items_kwargs, bloodline=item.bloodline)


class PackFile(PackDirStructure):
    _name: str = 'pack_file'

    _logger = None
    request_arg_group = {
        'url': ('field', 'http://3w62j02804.wicp.vip:66/api/raw/{path}'),
        'proxies': ('fixed', default_proxy_config),
        'cookies': ('field_json', '{cookies_json}'),
        'headers': ('field_json', '{headers_json}'),
        'is_leaf': ('fixed', True),
        'retry_limit': ('fixed', 3),
        'timeout': ('fixed', None),
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

if __name__ == '__main__':
    # MyItemType.start(ids=ids, items_kwargs=items_kwargs, bloodline=[])
    # path_md5 = hashlib.md5('.'.encode('utf-8')).hexdigest()[:12]
    PackDirStructure.start(ids='root', path='.', cookies_json=default_cookies_json, headers_json=default_headers_json, bloodline=[])
    pass