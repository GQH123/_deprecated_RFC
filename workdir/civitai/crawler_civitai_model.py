import os
os.environ['CURL_CA_BUNDLE'] = ''

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
    'http': 'http://127.0.0.1:20000',
    'https': 'http://127.0.0.1:20000',
    'all': 'socks5://127.0.0.1:20000',
}


class CivitaiModelDownload(ItemType):
    _name: str = 'itemtype_civitai_model_download'

    _logger = None
    request_arg_group = {
        'url': ('field', '{downloadURL}'),
        'proxies': ('fixed', default_proxy_config),
        'headers': ('fixed', {}),
        'is_leaf': ('fixed', True),
        'retry_limit': ('fixed', 5),
        'user_agent': ('none'),
        'referer': ('none'),
        'cookies': ('none'),
        # 'cookies': ('fixed', {
        #     '__stripe_mid': '4de85e89-e7ad-4055-ace9-cec2416a182913e741',
        #     'mode': 'All',
        #     'ref_landing_page': '%2F',
        #     '__Host-next-auth.csrf-token': '94e9c1bc739be2deedd18078630be9e6bed24d4a77ad426399035863cbbde35e%7C848403e72c16b8d7780300f1ca4fba70c8a6f3ac2350d50728215c16caf42e93',
        #     '__Secure-next-auth.callback-url': 'https%3A%2F%2Fcivitai.com%2Flogin%3FreturnUrl%3D%2F',
        #     '__Secure-civitai-token': 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..Mbo3U_IkVAAWZxmp.pXJ_9BlOQUNkjHaq46fGuzKzVmm9iY8bI3rDpk9BmT7TLw4QgFOdcCoo_8gX88W6JNuw7Vbis68zyCbR6tc3uj8yK9RURZd8YQxUkalqE8TUdb01jldliZXXahQ-WS6LXR332_B0cwa4EMyviuJfG0_-ZnvUkqOOepRYT5u6rIMbwraIr0NFv-AiolwjZ5bKlO9MlIrbetWy4si4PLQK12gAy9g1k2J31LDTbux5YDr7vZSVuHJCGSMgGzVjOUlnTL-OXIv8WkLeyRlhNM6Wlq1IyFnE-KXWak5mt-KLaPcdPahpCO85t2LHCbY3-aEHRBRJjo0SPO5cmebJZNuBUh2OhHLnmGpd1ULp5Mc0oRnYs4SThbGwf1LSF0uZFj1eqz-3MvCjzNzZFpRQPyE-YfxPv7XGDhTnf_rkdukn_bIOm8YkNDM-WA87CI5ODYw108vJ2pUNdAL4-6nV_bK-XDUk3ZBTZZmS8LxRETwUmx_bhwsunjJKO4Fm7QBjoU-TXlNejZTZTYeQITeOV3XebKy5vvaAnc3usud1uaSCZ-muE_N2SRRY2jIoz9UscRRwXDFJrGdku2ZP0ykAZ3ZZitll6VxtSgl7La_8-svXROom0t7SDxfPZ3cIaL1QfVYl-b_DnFQQ9BcX0qkmyRUmEfNJ2PUNPZQOoGtHFk1ItT9EO92KA2-4yjsUlBiCilBjrRjWYV5LkHCKEM2JvVIS9u9VMk6-uvjw4OaNRK7Sz7wsPs8xnbTV1fgsQao3GIWJQ2yrhGKO9iOplRTuCIqWsQ9dsnMA4rkmlIBscgS6KzK_TO_I9Rj2jQudYNBY6CyEQPKUZ3f1krzb3T39vh8wrhkZoTgYN2X5uWAFpXNV5C0wMpB5jcXWGexuGVjFdUe5PMOCYqbsfRelfJzN4WqNIXIFU5C94rPiUWEKo3FhEHghRG1GJFc-fwGNDiZux4VQKXR4O0WORfUwews9rDOmgFzMdMY2_N9GZ6L476Mi-OPzEWtfuyu2QEB1khiJcvQuNoUbLG7PE1axhDXd_o55ITxuqocJ-5PHpvy0179D6pw0crN0tOn9K0FyW0-6pl2K76R32U0jHHxUwqvz0xWemybVMneCrvG6bCzdxVtAvJpbpURsPz5fAfUDgDsiKge8MY6s8cavftKPsxCU1WKRtU6JxTUaWraeXVB0gn9bMZNwSwXqRkA.lsfPKbbzezjJ8aBdmyliJg',
        #     '__stripe_sid': 'b3c2913e-672f-49e4-97de-868493b49893c50b2c'
        # }),
        # 'cookies': ('fixed', {
        #     '__Host-next-auth.csrf-token': '3896e2ec4c6e88888f06f378c4c7e5900fced0d8ee19b262d8b33f0dcf5afe68%7C57545ce748bf7cc480ec7e0fce337f9d1dd95b29351b66d93f1162e8644504f5',
        #     'ref_landing_page': '%2F',
        #     '__stripe_mid': '64d639c2-55cf-4459-ab62-0596e36ff00c2bb83e',
        #     '__stripe_sid': '2794f726-a076-4e45-bb25-7a46fd5bc197bb3730',
        #     'blur': 'true',
        #     '__Secure-next-auth.callback-url': 'https%3A%2F%2Fcivitai.com%2Flogin%3FreturnUrl%3D%2Fmodels%2F400657',
        #     'disableHidden': 'false',
        #     'nsfw': 'true',
        #     'level': '31',
        #     '__Secure-civitai-token': 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..Av4btABwBKyn4CMv.5_-07aiEZ7HKfAnGvLXoeLcFgNWP_lhXlN6ba84vaanPE3dwOWi8M3O7Qyicau3QSO0p4Ye53gAdNPBxl6EK8tgfcXNgdMgw4d_CnhgkQMJg2hte8tVrNofsTD9qXGCp8xYYHFT52D-Yu3Nnv2DUq_yL6N8tgWRPvi0MWQKrOCj0A2fhRiZn8syg6JLD9FV-bql6HviCEDp5sfsVfi9Z9lOJbp3J4h_sOWrwUCFxxSjKinxdUd0dOtaX3FLciSsMDpsXcohc03RMRCgC3mWccSB8a8_fEgcER7Gb_PVc09FW_JDr2ruNzS7jcL70_hxveOazmtmvIBQH3xoDacWF2YsEImLbgfBkfDhYmBEd8AmoUyZOZGDGtPxIeq2ir9cPpzER_mDzXvE9ZKzR3RtbK8TbTFggmwdvb-5_vvmwe_CLjhe0m8g1FEYHyeYqQz_lQingTnxxjh7S31KNj0piqi9Ck6MS3G33Sa0vlfXb4W4vWSPLWWXntuHMM24x1U_D_t14Qb_9N6OmWu2410FB3B5tQKW2nCoLk5-4felyc7BTV2jlU1RG94Pxbz1JVmvO7NJiACvbjKRSdkGmAJLbBYxCAYCKnSVFBdCC6M-Gcs6WjKxsMFOE2-bJKen3uxiUA-bRxpnJ5KPO8loKb8AunjMms-rywwdDmx3U8J4J8IJd3jnbQEbmbwK5a6YcAboGNdTTUIVWXXuTIypKURCeqQFKv7npwcl37RxF4BJWtJlLDPLSyqlh5870-bFFOhtNdyXkQP0d06vO4tHSZizP-CZoLsH2qTYah8L13RqzUqSlH8KiqQaJQ_8PixbDH3bAxT3IKzTnChPoVBSb_PrVtOMsfC1UlHd7ASpXLykJkUNML1nRS9WYh6R0orbefMbMkFpnZ_ylvHanDJxDq57_R4RHcX2co76S5DvYkG1ctcRW3IV6G7KHkvB7YWM7OlERnHcEBOObTbZBBP8iPinRQoiL3dAsuE0PnFCzRJL15GILOLVmh5czJi6pNcs3fQ.KzsybIezFJpkUto1-fFAtw',
        # }),
        'timeout': ('fixed', 600),
    }
    item_arg_group = {
        'save_dir': ('auto', 'saves/models/{model_type}/{model_id}', 'subs'),
    }
    session_args = {
        'no_session': True,
        'lib': 'requests',
    }
    middleware_args = {
        'status_code': {
            'expected_status_codes': [200, 410, 404],
            # 410 Gone: Model archived, not available for download
            # 404 Not Found: File not found
            # 429 Too Many Requests: Rate limit
            # 401 Unauthorized: Login required
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


download_types = []
download_types += ['VAE', 'TextualInversion', 'Workflows', 'Wildcards', 'DoRA']
download_types += ['LORA', 'LoCon']
# download_types += ['Upscaler', 'AestheticGradient', 'Poses', 'MotionModule', 'Controlnet', 'Hypernetwork', 'Other']
ids = []
items_kwargs = []
for type in download_types:
    data = json.load(open(f'saves/links/{type}_links.json'))
    for model in data['models']:
        model_id = model.split(' ~ ')[-1].split('/')[-1]
        for i, link in enumerate(data['models'][model]):
            download_link = link.split(' ~ ')[-1]
            download_id = download_link.split('/')[-1]
            download_version = ' ~ '.join(link.split(' ~ ')[:-1])
            items_kwargs.append({
                'model_id': model_id,
                'model_type': type,
                'downloadURL': download_link,
            })
            ids.append(f'{download_id}_{download_version}')

CivitaiModelDownload._add_items(ids=ids, items_kwargs=items_kwargs, bloodline=[])
# CivitaiModelDownload._add_items(ids='303148_v1.0', model_id='268883', model_type='Wildcards', downloadURL='https://civitai.com/api/download/models/303148')
CivitaiModelDownload.start()