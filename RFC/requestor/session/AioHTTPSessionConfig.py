
from dataclasses import dataclass, field

from .SessionConfig import SessionConfig


@dataclass
class AioHTTPSessionConfig(SessionConfig):
    total_timeout: float | None = field(default=None)
    connect_timeout: float | None = field(default=None)
    sock_connect_timeout: float | None = field(default=None)
    sock_read_timeout: float | None = field(default=None)
    connections: int = field(default=1)
    connections_per_host: int = field(default=0)
    framework: str = 'aiohttp'
    use_async: bool = True
    async_framework: str = 'asyncio'