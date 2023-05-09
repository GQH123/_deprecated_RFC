from dataclasses import dataclass, field

from RFC.utils.BaseConfig import BaseConfig


@dataclass
class BaseProjectConfig(BaseConfig):
    project_name: str
    _project_name: str = field(init=False, repr=False)

    project_raw_path: str
    _project_raw_path: str = field(init=False, repr=False, default='/raw')

    project_config_path: str
    _project_config_path: str = field(init=False, repr=False, default='./configs')

    project_result_path: str
    _project_result_path: str = field(init=False, repr=False, default='./saves')

    project_log_path: str
    _project_log_path: str = field(init=False, repr=False, default='./logs')

    project_info_path: str
    _project_info_path: str = field(init=False, repr=False, default='./project_info.json')

    project_run_log_path: str
    _project_run_log_path: str = field(init=False, repr=False, default='./project_run.log')

    debug: bool
    _debug: bool = field(init=False, repr=False, default=False)

    project_debug_log_path: str
    _project_debug_log_path: str = field(init=False, repr=False, default='./project_debug.log')

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.project_name, property):
            self._project_name = '<unknown>'
        if isinstance(self.project_raw_path, property):
            self._project_raw_path = '/raw'
        if isinstance(self.project_config_path, property):
            self._project_config_path = './configs'
        if isinstance(self.project_result_path, property):
            self._project_result_path = './saves'
        if isinstance(self.project_log_path, property):
            self._project_log_path = './logs'
        if isinstance(self.project_info_path, property):
            self._project_info_path = './project_info.json'
        if isinstance(self.project_run_log_path, property):
            self._project_run_log_path = './project_run.log'
        if isinstance(self.debug, property):
            self._debug = False
        if isinstance(self.project_debug_log_path, property):
            self._project_debug_log_path = './project_debug.log'
    
    @property
    def project_name(self):
        return self._project_name
    
    @project_name.setter
    def project_name(self, value: str):
        self._project_name = value

    @property
    def project_raw_path(self):
        return self._project_raw_path

    @project_raw_path.setter
    def project_raw_path(self, value: str):
        self._project_raw_path = value

    @property
    def project_config_path(self):
        return self._project_config_path
    
    @project_config_path.setter
    def project_config_path(self, value: str):
        self._project_config_path = value

    @property
    def project_result_path(self):
        return self._project_result_path
    
    @project_result_path.setter
    def project_result_path(self, value: str):
        self._project_result_path = value

    @property
    def project_log_path(self):
        return self._project_log_path
    
    @project_log_path.setter
    def project_log_path(self, value: str):
        self._project_log_path = value

    @property
    def project_info_path(self):
        return self._project_info_path
    
    @project_info_path.setter
    def project_info_path(self, value: str):
        self._project_info_path = value

    @property
    def project_run_log_path(self):
        return self._project_run_log_path
    
    @project_run_log_path.setter
    def project_run_log_path(self, value: str):
        self._project_run_log_path = value

    @property
    def debug(self):
        return self._debug
    
    @debug.setter
    def debug(self, value: bool):
        self._debug = value

    @property
    def project_debug_log_path(self):
        return self._project_debug_log_path
    
    @project_debug_log_path.setter
    def project_debug_log_path(self, value: str):
        self._project_debug_log_path = value