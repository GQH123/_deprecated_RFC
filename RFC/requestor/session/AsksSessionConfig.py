from dataclasses import dataclass, field

from .SessionConfig import SessionConfig


@dataclass
class AsksSessionConfig(SessionConfig):
    connections: int = field(default=1)
    connection_timeout: int | float | None = field(default=60)
    persist_cookies: bool = field(default=False)
    framework: str = 'asks'
    use_async: bool = True
    async_framework: str = 'trio'