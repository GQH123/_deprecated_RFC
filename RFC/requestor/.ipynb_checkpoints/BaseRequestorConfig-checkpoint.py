from dataclasses import dataclass, field

from RFC.utils.functional_utils import BaseConfig

from .session.BaseSessionConfig import BaseSessionConfig


@dataclass
class BaseRequestorConfig(BaseConfig):
    framework: str = field(default='requests')
    use_session: bool = field(default=True)
    session_config: str | BaseSessionConfig = field(default_factory=BaseSessionConfig)