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

from RFC.requestor.middleware.middleware import get_middleware

from RFC.requestor.middleware.MiddleWareConfig import MiddleWareConfig
from RFC.requestor.middleware.JSONMiddleWareConfig import JSONMiddleWareConfig
from RFC.requestor.middleware.SaveMiddleWareConfig import SaveMiddleWareConfig
from RFC.requestor.middleware.StatusCodeMiddleWareConfig import StatusCodeMiddleWareConfig
from RFC.requestor.middleware.SaveBinaryMiddleWareConfig import SaveBinaryMiddleWareConfig

# ===============================================================================

from RFC.requestor.session.arguments.arguments import get_arguments

from RFC.requestor.session.arguments.ArgumentsConfig import ArgumentsConfig
from RFC.requestor.session.arguments.ArgumentsConfigMyProxy import ArgumentsConfigMyProxy

# ===============================================================================

from RFC.user.pipeline.PipelineConfig import PipelineConfig
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
    'middleware': MiddleWareConfig,
    'json': JSONMiddleWareConfig,
    'statuscode': StatusCodeMiddleWareConfig,
    'binary': SaveBinaryMiddleWareConfig,
    'save': SaveMiddleWareConfig,
    'arguments': ArgumentsConfig,
    'myproxy': ArgumentsConfigMyProxy,
    'noproxy': ArgumentsConfig,
    'project': ProjectConfig,
    'pipeline': PipelineConfig,
}

all_supported_module_types = {
    'itemset': get_itemset,
    'requestor': get_requestor,
    'session': get_session,
    'middleware': get_middleware,
    'arguments': get_arguments,
}


def _get_single_config(
    config_name: str,
    exact_match: bool = False,
):
    if not exact_match:
        config_name = config_name.lower()
        for config_part_name in all_supported_configs.keys():
            if config_part_name in config_name:
                return all_supported_configs[config_part_name]()
        raise NotSupported('config_name', config_name, all_supported_configs.keys(), __name__)
    else:
        for _, config_cls in all_supported_configs.items():
            if config_name == config_cls.__name__:
                return config_cls()
        raise NotSupported('config_name', config_name, [cls.__name__ for cls in all_supported_configs.values()], __name__)
    
    """
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
    elif 'middleware' in config_name:
        config = MiddleWareConfig()
    elif 'json' in config_name:
        config = JSONMiddleWareConfig()
    elif 'statuscode' in config_name:
        config = StatusCodeMiddleWareConfig()
    elif 'binary' in config_name:
        config = SaveBinaryMiddleWareConfig()
    elif 'save' in config_name:
        config = SaveMiddleWareConfig()
    elif 'myproxy' in config_name:
        config = ArgumentsConfigMyProxy()
    elif 'noproxy' in config_name:
        config = ArgumentsConfig()
    elif 'arguments' in config_name:
        config = ArgumentsConfig()
    elif 'project' in config_name:
        config = ProjectConfig()
    else:
        raise NotSupported('config_name', config_name, all_supported_configs.keys(), __name__)
    return config
    """


def get_config(
    config_name: str,
    exact_match: bool = False,
):
    return _get_single_config(config_name, exact_match)


def get_module(
    module_config: str | BaseConfig,
) -> BaseModule:
    if isinstance(module_config, str):
        module_config = _get_single_config(module_config)

    module_name = type(module_config).__name__
    if 'ItemsetConfig' in module_name:
        module = get_itemset(module_config)
    elif 'RequestorConfig' in module_name:
        module = get_requestor(module_config)
    elif 'SessionConfig' in module_name:
        module = get_session(module_config)
    elif 'MiddleWareConfig' in module_name:
        module = get_middleware(module_config)
    elif 'ArgumentsConfig' in module_name:
        module = get_arguments(module_config)
    else:
        raise NotSupported('module_name', module_name, all_supported_module_types.keys(), __name__)
    return module

