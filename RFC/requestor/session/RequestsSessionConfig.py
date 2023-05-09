from dataclasses import dataclass, field

from .SessionConfig import SessionConfig


@dataclass
class RequestsSessionConfig(SessionConfig):
    connect_timeout: int | float | None = field(default=None)  # 5
    read_timeout: int | float | None = field(default=None)  # 10
    framework: str = 'requests'
    use_async: bool = False