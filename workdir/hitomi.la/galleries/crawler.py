import urllib.parse

from RFC.item.item import ItemType


default_proxy_config = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
    'all': 'socks5://127.0.0.1:7890',
}


class HitomiGallery(ItemType):
    _name: str = 'itemtype_hitomi_gallery'

    _logger = None
    request_arg_group = {
        'url': ('field', 'https://ltn.hitomi.la/galleries/{id}.js'),
        'proxies': ('fixed', default_proxy_config),
        'referer': ('field', 
            'https://ltn.hitomi.la/artist/mutou mato-all.nozomi'
        ),
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
            'expected_status_codes': [200, 404],
        },
        'basic': {},
        'text_saver': {},
        'result_saver': {},
    }
    requestor_args = {
        'nproc': 12,
        'async_sema': 30,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 10,
    }
    
    @classmethod
    def _generate(cls, item, result):
        pass


# ids = [urllib.parse.quote_plus(id) for id in ids]
HitomiGallery.start(range(2815000))