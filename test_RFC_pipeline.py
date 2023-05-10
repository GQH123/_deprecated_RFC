#!/usr/bin/env python
# coding: utf-8

# In[1]:


from RFC import *


PixivArtworkInfo_Config = PipelineConfig(
    requestor_name='PixivArtworkInfoCrawler',
    verbose=True,
    user_project_config=dict(
        version='project',
        project_name="PixivArtworkInfo",
    ),
    user_itemset_config=dict(
        items=list(range(200010, 200020)),
        preprocess=None,
        attrs={
            'url': lambda i, x: f'https://www.pixiv.net/ajax/illust/{x}',
            'method': 'get',
            'name': lambda i, x: f'illust_{x}',
        },
        shuffle=True,
    ),
    user_arguments_config=dict(
        version='arguments-noproxy',
        config={
            'cookies': {
                'method': 'passin',
                'kwargs': {
                    'cookies': {
                        'PHPSESSID': '1234567890abcdef1234567890abcdef',
                        'device_token': '1234567890abcdef1234567890abcdef',
                    },
                    'ctype': dict,
                },
            },
            'proxies': {
                'method': 'passin',
                'kwargs': {
                    'proxies': {
                        'http': 'http://10.176.50.14:7890',
                        'https': 'http://10.176.50.14:7890',
                    },
                    'ptype': str,
                },
            },
        },
    ),
    user_middleware_config=[
        dict(
            version='json',
            savename=lambda item: f'{item.name}.json',
            mode='json',
        ),
    ],
    user_session_config=dict(
        version='requests',
        connect_timeout=20,
        read_timeout=10,
    ),
)

"""
    user_session_config=dict(
        version='aiohttp',
        total_timeout=20,
        connections=10,
        connections_per_host=10,
    ),
    user_session_config=dict(
        version='asks',
        connections=10,
        request_timeout=10,
        connection_timeout=10,
    ),
"""

PixivArtworkInfo_Pipeline = Pipeline(PixivArtworkInfo_Config)
PixivArtworkInfo_Pipeline.run()