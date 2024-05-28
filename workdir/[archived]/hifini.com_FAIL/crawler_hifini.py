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

# default_proxy_config = {
#     'http': 'http://10.176.52.116:7890',
#     'https': 'http://10.176.52.116:7890',
#     'all': 'socks5://10.176.52.116:7890',
# }


class HiFiNiPostPage(ItemType):
    _name: str = 'hifini_post_page'

    _logger = None
    request_arg_group = {
        'url': ('field', 'https://www.hifini.com/thread-{id}.htm'),
        'proxies': ('qgnet', 'D6FL1CJ8', '9FC1ADB88090'),
        'timeout': ('fixed', 60),
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
        'nproc': 6,
        # 'async_sema': 48,
        'async_sema': 6,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 10,
    }
    
    @classmethod
    def _generate(cls, item, result):
        # return  # two-stage mode
        def get_music_keys_and_links(text):
            music_keys = re.findall("url: 'get_music.php\?key=(.*)',", text)
            music_links = [f'https://www.hifini.com/get_music.php?key={key}' for key in music_keys]
            music_keys = [key.replace('/', '_') for key in music_keys]
            # it is very important to remove any possible '/', otherwise the whole framework will crash
            return music_keys, music_links
        
        try:
            music_keys, music_links = get_music_keys_and_links(result.content.decode('utf-8'))
            items_kwargs = [{'music_link': link} for link in music_links]
            HiFiNiMusicPreview._add_items(ids=music_keys, items_kwargs=items_kwargs, bloodline=item.bloodline)
        except Exception as e:
            cls._logger.error(f'Error in get_music_keys_and_links: [{type(e)}] {e}')
            return

class HiFiNiMusicPreview(HiFiNiPostPage):
    _name: str = 'hifini_music_preview'
    
    _logger = None
    request_arg_group = {
        'url': ('field', '{music_link}'),
        'proxies': ('qgnet', 'D6FL1CJ8', '9FC1ADB88090'),
        'is_leaf': ('fixed', True),
        'timeout': ('fixed', 60),
    }
    
    @classmethod
    def _generate(cls, item, result):
        pass


if __name__ == '__main__':
    ids = range(380000)
    HiFiNiPostPage._add_items(ids)  # in case adder is much slower than processes
    HiFiNiPostPage.start()