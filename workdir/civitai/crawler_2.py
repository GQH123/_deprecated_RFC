import os
import json
import time
import requests

from RFC.item.item import ItemType
from RFC.utils.parse import (
    parse,
    get_html_soup
)
from RFC.utils.func import save_object


default_proxy_config = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
    'all': 'socks5://127.0.0.1:7890',
}


class CivitaiModelDownload(ItemType):
    _name: str = 'itemtype_civitai_model_download'

    _logger = None
    request_arg_group = {
        'url': ('field', '{downloadURL}'),
        'proxies': ('fixed', {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890',
        }),
        'headers': ('fixed', {}),
        'is_leaf': ('fixed', True),
        'retry_limit': ('fixed', 5),
        'user_agent': ('none'),
        'referer': ('none'),
        'cookies': ('fixed', {
            '__stripe_mid': '4de85e89-e7ad-4055-ace9-cec2416a182913e741',
            'mode': 'All',
            'ref_landing_page': '%2F',
            '__Host-next-auth.csrf-token': '94e9c1bc739be2deedd18078630be9e6bed24d4a77ad426399035863cbbde35e%7C848403e72c16b8d7780300f1ca4fba70c8a6f3ac2350d50728215c16caf42e93',
            '__Secure-next-auth.callback-url': 'https%3A%2F%2Fcivitai.com%2Flogin%3FreturnUrl%3D%2F',
            '__Secure-civitai-token': 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..Mbo3U_IkVAAWZxmp.pXJ_9BlOQUNkjHaq46fGuzKzVmm9iY8bI3rDpk9BmT7TLw4QgFOdcCoo_8gX88W6JNuw7Vbis68zyCbR6tc3uj8yK9RURZd8YQxUkalqE8TUdb01jldliZXXahQ-WS6LXR332_B0cwa4EMyviuJfG0_-ZnvUkqOOepRYT5u6rIMbwraIr0NFv-AiolwjZ5bKlO9MlIrbetWy4si4PLQK12gAy9g1k2J31LDTbux5YDr7vZSVuHJCGSMgGzVjOUlnTL-OXIv8WkLeyRlhNM6Wlq1IyFnE-KXWak5mt-KLaPcdPahpCO85t2LHCbY3-aEHRBRJjo0SPO5cmebJZNuBUh2OhHLnmGpd1ULp5Mc0oRnYs4SThbGwf1LSF0uZFj1eqz-3MvCjzNzZFpRQPyE-YfxPv7XGDhTnf_rkdukn_bIOm8YkNDM-WA87CI5ODYw108vJ2pUNdAL4-6nV_bK-XDUk3ZBTZZmS8LxRETwUmx_bhwsunjJKO4Fm7QBjoU-TXlNejZTZTYeQITeOV3XebKy5vvaAnc3usud1uaSCZ-muE_N2SRRY2jIoz9UscRRwXDFJrGdku2ZP0ykAZ3ZZitll6VxtSgl7La_8-svXROom0t7SDxfPZ3cIaL1QfVYl-b_DnFQQ9BcX0qkmyRUmEfNJ2PUNPZQOoGtHFk1ItT9EO92KA2-4yjsUlBiCilBjrRjWYV5LkHCKEM2JvVIS9u9VMk6-uvjw4OaNRK7Sz7wsPs8xnbTV1fgsQao3GIWJQ2yrhGKO9iOplRTuCIqWsQ9dsnMA4rkmlIBscgS6KzK_TO_I9Rj2jQudYNBY6CyEQPKUZ3f1krzb3T39vh8wrhkZoTgYN2X5uWAFpXNV5C0wMpB5jcXWGexuGVjFdUe5PMOCYqbsfRelfJzN4WqNIXIFU5C94rPiUWEKo3FhEHghRG1GJFc-fwGNDiZux4VQKXR4O0WORfUwews9rDOmgFzMdMY2_N9GZ6L476Mi-OPzEWtfuyu2QEB1khiJcvQuNoUbLG7PE1axhDXd_o55ITxuqocJ-5PHpvy0179D6pw0crN0tOn9K0FyW0-6pl2K76R32U0jHHxUwqvz0xWemybVMneCrvG6bCzdxVtAvJpbpURsPz5fAfUDgDsiKge8MY6s8cavftKPsxCU1WKRtU6JxTUaWraeXVB0gn9bMZNwSwXqRkA.lsfPKbbzezjJ8aBdmyliJg',
            '__stripe_sid': 'b3c2913e-672f-49e4-97de-868493b49893c50b2c'
        }),
        'timeout': ('fixed', 600),
    }
    item_arg_group = {
        'save_dir': ('auto', 'saves/models/{model_type}/{model_id}', 'subs'),
    }
    session_args = {
        'no_session': False,
        'lib': 'requests',
    }
    middleware_args = {
        'status_code': {
            'expected_status_codes': [200, 410, 404],
            # 410 Gone: Model archived, not available for download
            # 404 Not Found: File not found
        },
        'basic': {},
        'content_saver': {},
        'result_saver': {},
    }
    requestor_args = {
        'nproc': 6,
        'async_sema': 6,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 10,
    }
    
    @classmethod
    def _generate(cls, item, result):
        pass


# download_types = ['VAE', 'TextualInversion', 'Workflows', 'Wildcards']
download_types = ['LORA', 'LoCon']
for type in download_types:
    data = json.load(open(f'scripts/{type}_links.json'))
    for model in data['models']:
        model_id = model.split(' ~ ')[-1].split('/')[-1]
        for i, link in enumerate(data['models'][model]):
            download_link = link.split(' ~ ')[-1]
            download_id = download_link.split('/')[-1]
            download_version = ' ~ '.join(link.split(' ~ ')[:-1])
            CivitaiModelDownload._add_items(ids=f'{download_id}_{download_version}', model_id=model_id, model_type=type, downloadURL=download_link)

# CivitaiModelDownload._add_items(ids='303148_v1.0', model_id='268883', model_type='Wildcards', downloadURL='https://civitai.com/api/download/models/303148')
CivitaiModelDownload.start()