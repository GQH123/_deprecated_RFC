import os
import inspect
from datetime import datetime
from functools import partial

from RFC.user.user import get_config, launch_project, get_module
from RFC.utils.BaseModule import BaseModule
from RFC.utils.functional_utils import log, save_object
from RFC.utils.exception_utils import ParamValueError

from .BasePipelineConfig import BasePipelineConfig


class BasePipeline(BaseModule):
    def _save_config(
        self,
    ):
        _frame = inspect.stack()[2]
        config_file_path = os.path.realpath(_frame[0].f_code.co_filename)
        with open(config_file_path, 'r') as f:
            config_file_content = f.read()
        save_object(
            config_file_content,
            f"{self.project_config.project_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.py",
            'config',
            mode = 'text',
        )
        
    def _init_attr(
        self,
        pipeline_config: BasePipelineConfig,
    ):
        self.logger = partial(log, file=['stdout'], mode='info', note='Pipeline', from_module=__name__)
        self.warner = partial(log, file=['stdout'], mode='warning', note='Pipeline', from_module=__name__)
        self.verbose = pipeline_config.verbose

    def _init_project(
        self,
        user_project_config: dict,
    ):
        self.user_project_config = user_project_config.copy()
        self.logger('initializing project...\n')
        def get_project_config():
            all_supported_project_type = ['project']
            project_type = user_project_config.pop('version', 'project')
            if project_type not in all_supported_project_type:
                raise ParamValueError('project_type', project_type, all_supported_project_type)
            project_config = get_config(project_type)
            project_config = project_config(**user_project_config)
            if self.verbose:
                project_config.print()
            return project_config

        self.project_config = get_project_config()
        self.project_info = launch_project(self.project_config)

    def _init_itemset(
        self,
        user_itemset_config: dict,
    ):
        self.user_itemset_config = user_itemset_config.copy()
        self.logger('initializing itemset...\n')
        def get_itemset_config():
            all_supported_itemset_type = ['rawitemset']
            itemset_type = user_itemset_config.pop('version', 'rawitemset')
            if itemset_type not in all_supported_itemset_type:
                raise ParamValueError('itemset_type', itemset_type, all_supported_itemset_type)
            itemset_config = get_config(itemset_type)
            itemset_config = itemset_config(**user_itemset_config)
            if self.verbose:
                itemset_config.print()
            return itemset_config
            

        self.itemset_config = get_itemset_config()
        self.itemset = get_module(self.itemset_config)
        if self.verbose:
            self.itemset.show()

    def _init_requestor(
        self,
        requestor_name: str,
        user_arguments_config: dict,
        user_middleware_config: dict,
        user_session_config: dict,
    ):
        self.requestor_name = requestor_name
        self.user_arguments_config = user_arguments_config.copy()
        self.user_middleware_config = user_middleware_config.copy()
        self.user_session_config = user_session_config.copy()
        self.logger('initializing requestor...\n')
        def get_arguments_config():
            all_supported_arguments_type = ['arguments-noproxy', 'arguments-qgnet-proxy']
            arguments_type = user_arguments_config.pop('version', 'arguments-noproxy')
            if arguments_type not in all_supported_arguments_type:
                raise ParamValueError('arguments_type', arguments_type, all_supported_arguments_type)
            arguments_config = get_config(arguments_type)
            arguments_config = arguments_config(**user_arguments_config)
            if self.verbose:
                arguments_config.print(include_sub=False)
            return arguments_config

        def get_session_config():
            all_supported_session_type = ['aiohttp', 'requests', 'asks']
            session_type = user_session_config.pop('version', 'requests')
            if session_type not in all_supported_session_type:
                raise ParamValueError('session_type', session_type, all_supported_session_type)
            if 'arguments_config' in user_session_config:
                self.warner('you should not provide arguments_config for session_config manually, it will be generated automatically, your arguments_config will be ignored.')
            if session_type == 'asks':
                self.warner('pay attention that asks does not support proxy, so if you provide proxy in arguments_config, it will be ignored.')
            session_config = get_config(session_type)
            user_session_config['arguments_config'] = get_arguments_config()
            session_config = session_config(**user_session_config)
            if self.verbose:
                session_config.print(include_sub=False)
            return session_config

        def get_middleware_config():
            nonlocal user_middleware_config 
            all_supported_middleware_type = ['json']
            if not isinstance(user_middleware_config, list):
                user_middleware_config = [user_middleware_config]
            middleware_configs = []
            for middleware_config in user_middleware_config:
                middleware_type = middleware_config.pop('version', 'json')
                if middleware_type not in all_supported_middleware_type:
                    raise ParamValueError('middleware_type', middleware_type, all_supported_middleware_type)
                _middleware_config = get_config(middleware_type)
                _middleware_config = _middleware_config(**middleware_config)
                middleware_configs.append(_middleware_config)
            if self.verbose:
                for middleware_config in middleware_configs:
                    middleware_config.print(include_sub=False)
                    self.logger('', pure_output=True)
            return middleware_configs

        def get_requestor_config():  # does not support user config, it is generated automatically
            requestor_config = get_config('requestor')
            requestor_config = requestor_config(
                name=requestor_name,
                session_config=get_session_config(),
                middleware_config=get_middleware_config(),
            )
            if self.verbose:
                requestor_config.print(include_sub=False)
            return requestor_config

        self.requstor_config = get_requestor_config()
        self.requestor = get_module(self.requstor_config)

    def _init_all(
        self,
        pipeline_config: BasePipelineConfig,
    ):
        self._init_attr(pipeline_config)
        self._init_project(pipeline_config.user_project_config)
        self._init_itemset(pipeline_config.user_itemset_config)
        self._init_requestor(pipeline_config.requestor_name, pipeline_config.user_arguments_config, pipeline_config.user_middleware_config, pipeline_config.user_session_config)

    def __init__(
        self,
        pipeline_config: BasePipelineConfig,
    ):
        super().__init__(pipeline_config)
        self._init_all(pipeline_config)

    def run(
        self,
        nproc: int = 1,
        async_sema: int = 1,
        **kwargs,
    ):
        self._save_config()
        self.requestor.run(self.itemset, nproc, async_sema, **kwargs)
    
    def _retrieve_config(
        self,
        return_config: bool = False
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        my_attr.update({
            'verbose': self.verbose,
            'requestor_name': self.requestor_name,
            'user_arguments_config': self.user_arguments_config,
            'user_middleware_config': self.user_middleware_config,
            'user_session_config': self.user_session_config,
            'user_project_config': self.user_project_config,
            'user_itemset_config': self.user_itemset_config,
        })
        if return_config:
            return BasePipelineConfig(**my_attr)
        else:
            return my_attr