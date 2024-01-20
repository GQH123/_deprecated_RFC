from dataclasses import dataclass, field

from RFC.utils.BaseConfig import BaseConfig

from .session.SessionConfig import SessionConfig
from .middleware.MiddleWareConfig import MiddleWareConfig


@dataclass
class BaseRequestorConfig(BaseConfig):
    session_config: str | SessionConfig
    _session_config: str | SessionConfig = field(init=False, repr=False)

    middleware_config: list[str | MiddleWareConfig] | str | MiddleWareConfig
    _middleware_config: list[str | MiddleWareConfig | str | MiddleWareConfig] = field(init=False, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.session_config, property):
            self._session_config = SessionConfig()
        if isinstance(self.middleware_config, property):
            self._middleware_config = []

    @property
    def session_config(self):
        return self._session_config
    
    @session_config.setter
    def session_config(self, value: str | SessionConfig):
        self._session_config = value

    @property
    def middleware_config(self):
        return self._middleware_config
    
    @middleware_config.setter
    def middleware_config(self, value: list[str | MiddleWareConfig] | str | MiddleWareConfig):
        self._middleware_config = value
