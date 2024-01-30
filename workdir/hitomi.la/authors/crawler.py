from RFC.item.item import ItemType

class HitomiPage(ItemType):
    _name: str = 'itemtype_hitomi_page'

    _logger = None
    request_arg_group = {
        'url': ('replace_id', 'https://hitomi.la/artist/mutou%20mato-all.html?page={id}'),
        'proxies': ('fixed', {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890',
        }),
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
        'saver': {},
    }
    requestor_args = {
        'nproc': 5,
        'async_sema': 1,
    }
    
    @classmethod
    def _generate(cls, id, result):
        pass


HitomiPage.start(range(3), debug_n=3)