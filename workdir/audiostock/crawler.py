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
    'http': 'http://10.176.52.116:7890',
    'https': 'http://10.176.52.116:7890',
    'all': 'socks5://10.176.52.116:7890',
}


class AudioBookAudioPage(ItemType):
    _name: str = 'audio_book_audio_page'

    _logger = None
    request_arg_group = {
        'url': ('field', 'https://audiostock.jp/audio/{id}'),
        # 'proxies': ('fixed', default_proxy_config),
        'proxies': ('api', 'qgnet', 'D6FL1CJ8', '9FC1ADB88090'),
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
        'async_sema': 24,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 10,
    }
    
    @classmethod
    def _generate(cls, item, result):
        soup = get_html_soup(result.content)
        parse_config = {
            'audio_tags': {
                ('attr', 'div', 'class', 'list-tag', None): {
                    ('type', 'dd', None): {}
                },
            },
            'audio_tag_types': {
                ('attr', 'div', 'class', 'list-tag', None): {
                    ('type', 'dt', None): {
                        ('result', 'text', None): {},
                    }
                },
            },
            'audio_link': {
                ('attr', 'span', 'class', 'player-audio-left-btn play-button', 0): {},
            },
            'audio_tags_in_each_group': {
                ('attr', 'a', 'class', 'btn tag-normal', None): {},
            },
        }
        audio_link = parse(soup, parse_config['audio_link'], return_str=False, debug=False)[0]['data-audio_url']
        tag_types = parse(soup, parse_config['audio_tag_types'], return_str=False, debug=False)
        tag_groups = parse(soup, parse_config['audio_tags'], return_str=False, debug=False)
        assert len(tag_types) == len(tag_groups)
        parsed_tags = []
        for tag_group in tag_groups:
            tags = parse(tag_group, parse_config['audio_tags_in_each_group'], return_str=False, debug=False)
            tags_link = [tag['href'] for tag in tags]
            tags_text = [tag.text for tag in tags]
            assert len(tags_link) == len(tags_text)
            tags = list(zip(tags_text, tags_link))
            parsed_tags.append(tags)
        assert len(parsed_tags) == len(tag_types)
        tag_result = {tag_type: tags for tag_type, tags in zip(tag_types, parsed_tags)}
        result = {
            'audio_link': audio_link,
            'audio_tags': tag_result,
        }
        json.dump(result, open(os.path.join(item.save_dir, f'{item.id}.json'), 'w'), indent=4, ensure_ascii=False)
        AudioBookAudioFile._add_items([item.id], url=audio_link, bloodline=item.bloodline)


class AudioBookAudioFile(AudioBookAudioPage):
    _name: str = 'audio_book_audio_file'
    
    _logger = None
    request_arg_group = {
        'url': ('field', '{url}'),
        'proxies': ('fixed', default_proxy_config),
        'is_leaf': ('fixed', True),  # in case the binary data is saved twice
    }
    
    @classmethod
    def _generate(cls, item, result):
        pass


# AudioBookAudioPage.start(ids=list(range(1000, 1100)))
AudioBookAudioPage.start(ids=list(range(1540000)))