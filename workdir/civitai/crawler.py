import re
import json
import time
import requests

from RFC.item.item import ItemType


default_proxy_config = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
    'all': 'socks5://127.0.0.1:7890',
}


class HitomiAuthor(ItemType):
    _name: str = 'itemtype_hitomi_author'

    _logger = None
    request_arg_group = {
        'url': ('field', 'https://ltn.hitomi.la/artist/{id}-all.nozomi'),
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
        'nproc': 1,
        'async_sema': 24,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 10,
    }
    
    @classmethod
    def _generate(cls, item, result):
        def decode_gallery_id(bytes):
            assert len(bytes) % 4 == 0, f'length of bytes {len(bytes)} not divisible by 4'
            ids = []
            for i in range(0, len(bytes), 4):
                ids.append(int.from_bytes(bytes[i:i+4], 'big'))
            return ids
        ids = decode_gallery_id(result['content'])
        HitomiGallery._add_items(ids, ancestor_id=item.id, bloodline=item.bloodline)


class HitomiGallery(HitomiAuthor):
    _name: str = 'itemtype_hitomi_gallery'

    _logger = None
    request_arg_group = {
        'url': ('field', 'https://ltn.hitomi.la/galleries/{id}.js'),
        'proxies': ('fixed', {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890',
        }),
        'referer': ('field', 
            'https://ltn.hitomi.la/artist/{ancestor_id}-all.nozomi'
        ),
    }
    
    @classmethod
    def _generate(cls, item, result):
        def _request_prefix():
            while True:
                try:
                    resp = requests.get('https://ltn.hitomi.la/gg.js', proxies=default_proxy_config, headers={'referer': 'https://hitomi.la/reader/509748.html'})
                    prefix = re.findall('b: \'([0-9]*)\/', resp.text)
                    value_o = [int(x) for x in re.findall('o = ([0-1])', resp.text)]
                    hit_hash = [int(x) for x in re.findall('case ([0-9]+):', resp.text)]
                    assert len(prefix) == 1 and len(value_o) == 2
                    return prefix[0], value_o, hit_hash
                except Exception as e:
                    time.sleep(1)
            
        def _from_hash_to_url(hash, prefix):
            return f'{prefix}/{int(hash[-1]+hash[-3:-1], 16)}/{hash}'
            # '1706601602/2151/b5ddc3da968890e7ef4b94982e286a8cd27319c9fbc4853012d5be6546ebc678'
            
        def _get_base(value_o, hit_hash, hash):
            o = value_o[-1] if int(hash[-1]+hash[-3:-1], 16) in hit_hash else value_o[0]
            return chr(ord('a')+o)

        def _add_image(id, img_type, img_hash, prefix, base):
            url = f'https://{base}a.hitomi.la/{img_type}/{_from_hash_to_url(img_hash, prefix)}.{img_type}'
            # https://aa.hitomi.la/avif/1706626802/824/55f3b7adf6924bd63d88d1d1d990d2ab3114d03be5adcf682ac56900a41b2383.avif
            HitomiImage._add_items([id], ancestor_id=item.id, bloodline=item.bloodline, url=url)

        js = result['content'].decode()
        assert js.startswith('var galleryinfo = ')
        js = json.loads(js[len('var galleryinfo = '):])
        prefix, value_o, hit_hash = _request_prefix()
        for id, img in enumerate(js['files']):
            hash = img['hash']
            id = f'{id:04d}'
            added = False
            base = _get_base(value_o, hit_hash, hash)
            if 'hasavif' in img and img['hasavif'] == 1:
                _add_image(id, 'avif', hash, prefix, base)
                added = True
            if 'haswebp' in img and img['haswebp'] == 1:
                _add_image(id, 'webp', hash, prefix, base)
                added = True
            if not added and 'hasjxl' in img and img['hasjxl'] == 1:  # optional
                _add_image(id, 'jxl', hash, prefix, base)
                added = True


class HitomiImage(HitomiGallery):
    _name: str = 'itemtype_hitomi_image'

    _logger = None
    request_arg_group = {
        'url': ('field', '{url}'),
        'proxies': ('fixed', {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890',
        }),
        'referer': ('field', 
            'https://hitomi.la/reader/{ancestor_id}.html'
        ),
        'headers': ('switch', 'none'),
        'is_leaf': ('fixed', True),
    }
    
    @classmethod
    def _generate(cls, item, result):
        pass


ids = ['xxx']
# ids = [urllib.parse.quote_plus(id) for id in ids]
HitomiAuthor.start(ids)