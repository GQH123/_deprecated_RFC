from dataclasses import dataclass, field

from RFC.utils.BaseConfig import BaseConfig


@dataclass
class BasePipelineConfig(BaseConfig):
    verbose: bool
    _verbose: bool = field(init=False, repr=False)

    requestor_name: str
    _requestor_name: str = field(init=False, repr=False)

    user_project_config: dict
    _user_project_config: dict = field(init=False, repr=False)

    user_itemset_config: dict
    _user_itemset_config: dict = field(init=False, repr=False)

    user_arguments_config: dict
    _user_arguments_config: dict = field(init=False, repr=False)

    user_session_config: dict
    _user_session_config: dict = field(init=False, repr=False)

    user_middleware_config: list[dict] | dict
    _user_middleware_config: list[dict] | dict = field(init=False, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.verbose, property):
            self._verbose = False
        if isinstance(self.requestor_name, property):
            self._requestor_name = 'MyRequestor'
        if isinstance(self.user_project_config, property):
            self._user_project_config = dict()
        if isinstance(self.user_itemset_config, property):
            self._user_itemset_config = dict()
        if isinstance(self.user_arguments_config, property):
            self._user_arguments_config = dict()
        if isinstance(self.user_session_config, property):
            self._user_session_config = dict()
        if isinstance(self.user_middleware_config, property):
            self._user_middleware_config = dict()
    
    @property
    def verbose(self):
        return self._verbose
    
    @verbose.setter
    def verbose(self, value: bool):
        self._verbose = value

    @property
    def requestor_name(self):
        return self._requestor_name
    
    @requestor_name.setter
    def requestor_name(self, value: str):
        self._requestor_name = value

    @property
    def user_project_config(self):
        return self._user_project_config

    @user_project_config.setter
    def user_project_config(self, value: dict):
        self._user_project_config = value

    @property
    def user_itemset_config(self):
        return self._user_itemset_config

    @user_itemset_config.setter
    def user_itemset_config(self, value: dict):
        self._user_itemset_config = value
    
    @property
    def user_arguments_config(self):
        return self._user_arguments_config
    
    @user_arguments_config.setter
    def user_arguments_config(self, value: dict):
        self._user_arguments_config = value

    @property
    def user_session_config(self):
        return self._user_session_config
    
    @user_session_config.setter
    def user_session_config(self, value: dict):
        self._user_session_config = value

    @property
    def user_middleware_config(self):
        return self._user_middleware_config
    
    @user_middleware_config.setter
    def user_middleware_config(self, value: list[dict] | dict):
        self._user_middleware_config = value