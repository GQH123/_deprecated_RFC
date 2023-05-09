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


config_help()


# In[2]:


def initialize_project():
    log('initializing project...\n', file=['stdout'], mode='info', note='Pipeline', from_module=__name__)
    def get_project_config():
        project_config = get_config('project')
        project_config = project_config(
            debug=True,
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
            items=list(range(200000, 210000)),
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
            },
        )
        # arguments_config.print()
        return arguments_config

    def get_session_config():
        session_config = get_config('aiohttp')
        session_config = session_config(
            name='MySession',
            arguments_config=get_arguments_config(),
            total_timeout=20,
            connections=10,
            connections_per_host=10,
        )
        # session_config.print(include_sub=True)
        return session_config

    def get_requestor_config():
        requestor_config = get_config('requestor')
        requestor_config = requestor_config(
            name='MyRequestor',
            session_config=get_session_config(),
        )
        requestor_config.print(include_sub=True)
        return requestor_config

    requstor_config = get_requestor_config()
    requestor = get_module(requstor_config)
    return requestor


requestor = get_requestor()


# In[ ]:


# Convert .ipynb to .py
import os

if __name__ == '__main__':
    os.system('jupyter nbconvert --to python test_RFC_pipeline.ipynb')

