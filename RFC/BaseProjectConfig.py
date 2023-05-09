from dataclasses import dataclass, field

from RFC.utils.BaseConfig import BaseConfig


@dataclass
class BaseProjectConfig(BaseConfig):
    project_name: str = field(default='<unknown>')
    project_raw_path: str = field(default='./raw')
    project_config_path: str = field(default='./configs')
    project_result_path: str = field(default='./saves')
    project_log_path: str = field(default='./logs')
    project_info_path: str = field(default='./project_info.json')
    project_run_log_path: str = field(default='./project_run.log')
    debug: bool = field(default=False)
    project_debug_log_path: str = field(default='./project_debug.log')