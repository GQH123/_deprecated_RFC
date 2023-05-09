from dataclasses import dataclass, field

from RFC.utils.BaseConfig import BaseConfig

from .session.SessionConfig import SessionConfig


@dataclass
class BaseRequestorConfig(BaseConfig):
    session_config: str | SessionConfig = field(default_factory=SessionConfig)