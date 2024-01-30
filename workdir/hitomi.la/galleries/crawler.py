import urllib.parse

from RFC.item.item import ItemType

class HitomiGallery(ItemType):
    _name: str = 'itemtype_hitomi_gallery'

    _logger = None
    request_arg_group = {
        'url': ('field', 'https://ltn.hitomi.la/galleries/{id}.js'),
        'proxies': ('fixed', {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890',
        }),
        'referer': ('field', 
            'https://ltn.hitomi.la/artist/mutou mato-all.nozomi'
        ),
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
        'nproc': 4,
        'async_sema': 1,
        'wait_timeout': 3,
    }
    
    @classmethod
    def _generate(cls, item, result):
        pass


# ids = [urllib.parse.quote_plus(id) for id in ids]
HitomiGallery.start(range(1000))