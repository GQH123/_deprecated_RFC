from dataclasses import dataclass, field

from .BaseRequestorConfig import BaseRequestorConfig
from .session.SessionConfig import SessionConfig


@dataclass
class RequestorConfig(BaseRequestorConfig):
    session_config: SessionConfig = field(default_factory=SessionConfig)
    ...