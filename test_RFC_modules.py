#!/usr/bin/env python
# coding: utf-8

# In[1]:


from RFC import *


def config_help():
    project_config_example = get_config('project')
    project_config_example.print()
    # itemset_config_example = get_config('rawitemset')
    # itemset_config_example.print()
    # arguments_config_example = get_config('arguments-noproxy')
    # arguments_config_example.print()
    aiohttp_session_config_example = get_config('aiohttp')
    aiohttp_session_config_example.print(include_sub=False)
    requestor_config_exmaple = get_config('requestor')
    requestor_config_exmaple.print(include_sub=False)
    middleware_config_example = get_config('json')
    middleware_config_example.print(include_sub=False)


config_help()


# In[2]:


def initialize_project():
    log('initializing project...\n', file=['stdout'], mode='info', note='Pipeline', from_module=__name__)
    def get_project_config():
        project_config = get_config('project')
        project_config = project_config(
            name='MyProject',
            project_debug_log_path="./project_debug.log",
            project_info_path="./project_info.json",
            project_name="MyFirstProject",
            project_run_log_path="./project_run.log",
        )
        project_config.print()
        return project_config

    project_config = get_project_config()
    launch_project(project_config)

initialize_project()


# In[3]:


def get_itemset():
    log('initializing itemset...\n', file=['stdout'], mode='info', note='Pipeline', from_module=__name__)
    def get_itemset_config():
        itemset_config = get_config('rawitemset')
        itemset_config = itemset_config(
            name='MyItemset',
            items=list(range(200010, 200020)),
            preprocess=None,
            attrs={
                'url': lambda i, x: f'https://www.pixiv.net/ajax/illust/{x}',
                'method': 'get',
                'name': lambda i, x: f'illust_{x}',
            },
            shuffle=True,
        )
        return itemset_config

    itemset_config = get_itemset_config()
    itemset = get_module(itemset_config)
    itemset.show()
    return itemset


itemset = get_itemset()


# In[4]:


def get_requestor():
    log('initializing requestor...\n', file=['stdout'], mode='info', note='Pipeline', from_module=__name__)

    def get_arguments_config():
        arguments_config = get_config('arguments-noproxy')
        arguments_config = arguments_config(
            name='MyArguments',
            config={
                'cookies': {
                    'kwargs': {
                        'cookies': {
                            'PHPSESSID': '1234567890abcdef1234567890abcdef',
                            'device_token': '1234567890abcdef1234567890abcdef',
                        },
                        'ctype': dict,
                    },
                    'method': 'passin',
                },
                'proxies': {
                    'kwargs': {
                        'proxies': {
                            'http': 'http://10.176.50.14:7890',
                            'https': 'http://10.176.50.14:7890',
                        },
                        'ptype': str,
                    },
                    'method': 'passin',
                },
            },
        )
        # arguments_config.print()
        return arguments_config

    def get_session_config():
        session_config = get_config('asks')
        session_config = session_config(
            name='MySession',
            arguments_config=get_arguments_config(),
            connections=10,
            request_timeout=10,
            connection_timeout=10,
        )
        """
        session_config = get_config('aiohttp')
        session_config = session_config(
            name='MySession',
            arguments_config=get_arguments_config(),
            total_timeout=20,
            connections=10,
            connections_per_host=10,
        )
        """
        """
        session_config = get_config('requests')
        session_config = session_config(
            name='MySession',
            arguments_config=get_arguments_config(),
            connect_timeout=20,
            read_timeout=10,
        )
        """
        # session_config.print(include_sub=True)
        return session_config

    def get_middleware_config():
        middleware_config = get_config('json')
        middleware_config = middleware_config(
            name='MyMiddleware',
            savename=lambda item: f'{item.name}.json',
            mode='json',
        )
        # middleware_config.print(include_sub=True)
        return middleware_config

    def get_requestor_config():
        requestor_config = get_config('requestor')
        requestor_config = requestor_config(
            name='MyRequestor',
            session_config=get_session_config(),
            middleware_config=get_middleware_config(),
        )
        requestor_config.print(include_sub=True)
        return requestor_config

    requstor_config = get_requestor_config()
    requstor_config.print()
    requestor = get_module(requstor_config)
    return requestor


requestor = get_requestor()

requestor.run(itemset)