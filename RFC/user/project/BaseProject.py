import os
import sys
from datetime import datetime

from RFC.utils.BaseModule import BaseModule
from RFC.utils.functional_utils import log, update_output_channels, load_object, save_object, get_prev_module_name, init_global_project_config, pretty_print_parser
from RFC.user.compile import run_compile

from .BaseProjectConfig import BaseProjectConfig


class BaseProject(BaseModule):
    def _init_attr(
        self,
        project_config: BaseProjectConfig,
    ):
        self.project_name = project_config.project_name
        self.project_error_path = project_config.project_error_path
        self.project_raw_path = project_config.project_raw_path
        self.project_config_path = project_config.project_config_path
        self.project_result_path = project_config.project_result_path
        self.project_log_path = project_config.project_log_path
        self.project_info_path = project_config.project_info_path
        self.project_run_log_path = project_config.project_run_log_path
        self.project_debug_log_path = project_config.project_debug_log_path
        self.project_root = os.path.abspath(self.project_name)
        # project_run_log_path = os.path.join(project_name, project_run_log_path)
        # project_info_path = os.path.join(project_name, project_info_path)
        # if debug:
        #     project_debug_log_path = os.path.join(project_name, project_debug_log_path)

        project_config.project_root = self.project_root
        init_global_project_config(project_config)
        
    def __init__(
        self,
        project_config: BaseProjectConfig,
    ):
        super().__init__(project_config)
        self._init_attr(project_config)

    def launch(
        self,
    ):
        os.system(f'rm -rf "{self.project_root}"')
        if not os.path.exists(self.project_root):
            os.makedirs(self.project_root)
        if not os.path.exists(os.path.join(self.project_root, self.project_error_path)):
            os.makedirs(os.path.join(self.project_root, self.project_error_path))
        if not os.path.exists(os.path.join(self.project_root, self.project_raw_path)):
            os.makedirs(os.path.join(self.project_root, self.project_raw_path))
        if not os.path.exists(os.path.join(self.project_root, self.project_config_path)):
            os.makedirs(os.path.join(self.project_root, self.project_config_path))
        if not os.path.exists(os.path.join(self.project_root, self.project_result_path)):
            os.makedirs(os.path.join(self.project_root, self.project_result_path))
        if not os.path.exists(os.path.join(self.project_root, self.project_log_path)):
            os.makedirs(os.path.join(self.project_root, self.project_log_path))

        run_compile()

        if os.path.exists(os.path.join(self.project_root, self.project_info_path)):
            project_info = load_object(os.path.join(self.project_root, self.project_info_path))
            project_info.update({
                'name': self.project_name,
                'error_path': self.project_error_path,
                'raw_path': self.project_raw_path,
                'config_path': self.project_config_path,
                'result_path': self.project_result_path,
                'log_path': self.project_log_path,
                'root': self.project_root,
                'info_path': self.project_info_path,
                'run_log_path': self.project_run_log_path,
                'debug_log_path': self.project_debug_log_path,
                # 'created_time': datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
                'last_launched_time': datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
            })
        else:
            project_info = {
                'name': self.project_name,
                'error_path': self.project_error_path,
                'raw_path': self.project_raw_path,
                'config_path': self.project_config_path,
                'result_path': self.project_result_path,
                'log_path': self.project_log_path,
                'root': self.project_root,
                'info_path': self.project_info_path,
                'run_log_path': self.project_run_log_path,
                'debug_log_path': self.project_debug_log_path,
                'created_time': datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
                'last_launched_time': datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
            }

        update_output_channels('test', sys.stdout)

        if self.project_run_log_path:
            update_output_channels('main', self.project_run_log_path)

        if self.project_debug_log_path:
            update_output_channels('debug', self.project_debug_log_path)

        save_object(project_info, self.project_info_path)
        log(f'Project {self.project_name} launched.\n', note='Project', mode='info', from_module=get_prev_module_name(1))
        log(f'Project Configurations:\n{pretty_print_parser(self.__dict__)}\n', pure_output=True)

    def _retrieve_config(
        self,
        return_config: bool = False
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        my_attr.update({
            'project_name': self.project_name,
            'project_error_path': self.project_error_path,
            'project_raw_path': self.project_raw_path,
            'project_config_path': self.project_config_path,
            'project_result_path': self.project_result_path,
            'project_log_path': self.project_log_path,
            'project_info_path': self.project_info_path,
            'project_run_log_path': self.project_run_log_path,
            'project_debug_log_path': self.project_debug_log_path,
        })
        if return_config:
            return BaseProjectConfig(**my_attr)
        else:
            return my_attr