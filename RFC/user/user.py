# ===============================================================================

# Author: Renatus & Copilot

# ===============================================================================

from RFC.utils.RootObject import RootObject
from RFC.utils.BaseConfig import BaseConfig
from RFC.utils.BaseModule import BaseModule

# ===============================================================================

from RFC.itemset.itemset import get_itemset

from RFC.itemset.RawItemsetConfig import RawItemsetConfig
from RFC.itemset.ItemsetConfig import ItemsetConfig

# ===============================================================================

from RFC.requestor.requestor import get_requestor

from RFC.requestor.RequestorConfig import RequestorConfig

# ===============================================================================

from RFC.requestor.session.session import get_session

from RFC.requestor.session.SessionConfig import SessionConfig
from RFC.requestor.session.RequestsSessionConfig import RequestsSessionConfig
from RFC.requestor.session.AsksSessionConfig import AsksSessionConfig
from RFC.requestor.session.AioHTTPSessionConfig import AioHTTPSessionConfig

# ===============================================================================

from RFC.requestor.session.arguments.arguments import get_arguments

from RFC.requestor.session.arguments.ArgumentsConfig import ArgumentsConfig
from RFC.requestor.session.arguments.ArgumentsConfigMyProxy import ArgumentsConfigMyProxy

# ===============================================================================

from RFC.user.launch import launch_project
from RFC.user.project.ProjectConfig import ProjectConfig

# ===============================================================================

from RFC.utils.exception_utils import NotSupported

# ===============================================================================


all_supported_configs = {
    'rawitemset': RawItemsetConfig,
    'itemset': ItemsetConfig,
    'requestor': RequestorConfig,
    'session': SessionConfig,
    'requests': RequestsSessionConfig,
    'asks': AsksSessionConfig,
    'aiohttp': AioHTTPSessionConfig,
    'arguments': ArgumentsConfig,
    'arguments-myproxy': ArgumentsConfigMyProxy,
    'project': ProjectConfig,
}

all_supported_module_types = {
    'itemset': get_itemset,
    'requestor': get_requestor,
    'session': get_session,
    'arguments': get_arguments,
}


def _get_single_config(
    config_name: str,
):
    config_name = config_name.lower()
    if 'rawitemset' in config_name:
        config = RawItemsetConfig()
    elif 'itemset' in config_name:
        config = ItemsetConfig()
    elif 'requestor' in config_name:
        config = RequestorConfig()
    elif 'session' in config_name:
        config = SessionConfig()
    elif 'requests' in config_name:
        config = RequestsSessionConfig()
    elif 'asks' in config_name:
        config = AsksSessionConfig()
    elif 'aiohttp' in config_name:
        config = AioHTTPSessionConfig()
    elif 'arguments-myproxy' in config_name:
        config = ArgumentsConfigMyProxy()
    elif 'arguments-noproxy' in config_name:
        config = ArgumentsConfig()
    elif 'arguments' in config_name:
        config = ArgumentsConfig()
    elif 'project' in config_name:
        config = ProjectConfig()
    else:
        raise NotSupported('config_name', config_name, all_supported_configs.keys(), __name__)
    return config


def get_config(
    config_name: str,
):
    return _get_single_config(config_name)


def get_module(
    module_config: str | BaseConfig,
):
    if isinstance(module_config, str):
        module_config = _get_single_config(module_config)

    module_name = type(module_config).__name__
    if 'ItemsetConfig' in module_name:
        module = get_itemset(module_config)
    elif 'RequestorConfig' in module_name:
        module = get_requestor(module_config)
    elif 'SessionConfig' in module_name:
        module = get_session(module_config)
    elif 'ArgumentsConfig' in module_name:
        module = get_arguments(module_config)
    else:
        raise NotSupported('module_name', module_name, all_supported_module_types.keys(), __name__)
    return module

