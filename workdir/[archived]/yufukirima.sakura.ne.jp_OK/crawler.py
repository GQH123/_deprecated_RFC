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


class FanboxPost(ItemType):
    _name: str = 'itemtype_fanbox_post'

    _logger = None
    request_arg_group = {
        'url': ('field', 'https://api.fanbox.cc/post.info?postId={id}'),
        'proxies': ('fixed', {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890',
        }),
        'headers': ('fixed', {
            'origin': 'https://www.fanbox.cc',
        }),
        'cookies': ('fixed', dict(
            p_ab_id='6',
            p_ab_id_2='8',
            p_ab_d_id='1921126919',
            privacy_policy_agreement='6',
            privacy_policy_notification='0',
            FANBOXSESSID='89975465_xSHr75TnOTiMsHaT6unE3UMXJNd8axyZ',
        )),
        'retry_limit': ('fixed', 3),  # this is the key series path, so failure will end the whole process, you can set this to be larger
    }
    item_arg_group = {
        'save_dir': ('auto', 'saves/posts/', 'subs'),
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
        'json_saver': {},
        'result_saver': {},
    }
    requestor_args = {
        'nproc': 12,
        'async_sema': 24,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 1,
    }
    
    @classmethod
    def _generate(cls, item, result):
        _json = result['json']['body']
        if _json['prevPost'] is not None:
            next_id = _json['prevPost']['id']
            if int(next_id) <= 7305540:
                return
            FanboxPost._add_items(next_id)  # next post, same level, no bloodline
        if 'coverImageUrl' in _json and _json['coverImageUrl'] is not None:
            FanboxPostImage._add_items(ids='cover', imageURL=_json['coverImageUrl'], ancestor_id=item.id, bloodline=item.bloodline)
        if 'imageForShare' in _json and _json['imageForShare'] is not None:
            FanboxPostImage._add_items(ids='share', imageURL=_json['imageForShare'], ancestor_id=item.id, bloodline=item.bloodline)
        if 'body' in _json and 'images' in _json['body'] and _json['body']['images'] is not None:
            for i, image in enumerate(_json['body']['images']):
                FanboxPostImage._add_items(ids=f'body_{i}', imageURL=image['originalUrl'], ancestor_id=item.id, bloodline=item.bloodline)


class FanboxPostImage(FanboxPost):
    _name: str = 'itemtype_fanbox_post_image'

    _logger = None
    request_arg_group = {
        'url': ('field', '{imageURL}'),
        'proxies': ('fixed', {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890',
        }),
        'referer': ('field', 
            'https://yufukirima.fanbox.cc/posts/{ancestor_id}'
        ),
        'is_leaf': ('fixed', True),
        'headers': ('fixed', {
            'origin': 'https://www.fanbox.cc',
        }),
        'cookies': ('fixed', dict(
            p_ab_id='6',
            p_ab_id_2='8',
            p_ab_d_id='1921126919',
            privacy_policy_agreement='6',
            privacy_policy_notification='0',
            FANBOXSESSID='89975465_xSHr75TnOTiMsHaT6unE3UMXJNd8axyZ',
        )),
    }
    middleware_args = {
        'status_code': {
            'expected_status_codes': [200],
        },
        'basic': {},
        'content_saver': {},
        'result_saver': {},
    }
    
    @classmethod
    def _generate(cls, item, result):
        pass


class YufukirimaGalleryImage(FanboxPost):
    _name: str = 'itemtype_yufukirima_gallery_image'

    _logger = None
    request_arg_group = {
        'url': ('field', '{imageURL}'),
        'proxies': ('fixed', {
            'http': 'http://127.0.0.1:7890',
            'https': 'http://127.0.0.1:7890',
        }),
        'referer': ('field', 
            'https://yufukirima.sakura.ne.jp/events/show.php'
        ),
        'is_leaf': ('fixed', True),
        'headers': ('fixed', {}),
        'cookies': ('fixed', {}),
        'retry_limit': ('fixed', 5),
    }
    middleware_args = {
        'status_code': {
            'expected_status_codes': [200],
        },
        'basic': {},
        'content_saver': {},
        'result_saver': {},
    }
    
    @classmethod
    def _generate(cls, item, result):
        pass


# newest_post_id = 7524520
# FanboxPost.start(newest_post_id)

# galleries = json.load(open('scripts/galleries.json', 'r'))
# for post in galleries:
#     print(post)
#     for i, link in enumerate(galleries[post]):
#         print(i, link)
#         YufukirimaGalleryImage._add_items(ids=f'gallery_{i}', imageURL=link, bloodline=[(FanboxPost.__name__, post)])
# YufukirimaGalleryImage.start()

galleries = json.load(open('scripts/galleries_extra.json', 'r'))
for post in galleries:
    print(post)
    for i, link in enumerate(galleries[post]):
        print(i, link)
        YufukirimaGalleryImage._add_items(ids=f'gallery_{i}', imageURL=link, bloodline=[(FanboxPost.__name__, post)])
YufukirimaGalleryImage.start()