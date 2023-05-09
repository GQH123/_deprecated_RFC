from dataclasses import dataclass, field

from RFC.utils.BaseConfig import BaseConfig

from .session.SessionConfig import SessionConfig


@dataclass
class BaseRequestorConfig(BaseConfig):
    session_config: str | SessionConfig
    _session_config: SessionConfig = field(init=False, repr=False)

    def __post_init__(self):
        if isinstance(self.session_config, property):
            self._session_config = SessionConfig()

    @property
    def session_config(self):
        return self._session_config
    
    @session_config.setter
    def session_config(self, value: str | SessionConfig):
        self._session_config = value