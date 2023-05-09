
from dataclasses import dataclass, field

from .SessionConfig import SessionConfig


@dataclass
class AioHTTPSessionConfig(SessionConfig):
    total_timeout: float | None
    _total_timeout: float | None = field(init=False, repr=False)

    connect_timeout: float | None
    _connect_timeout: float | None = field(init=False, repr=False)

    sock_connect_timeout: float | None
    _sock_connect_timeout: float | None = field(init=False, repr=False)

    sock_read_timeout: float | None
    _sock_read_timeout: float | None = field(init=False, repr=False)

    connections: int
    _connections: int = field(init=False, repr=False)

    connections_per_host: int
    _connections_per_host: int = field(init=False, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.total_timeout, property):
            self._total_timeout = None
        if isinstance(self.connect_timeout, property):
            self._connect_timeout = None
        if isinstance(self.sock_connect_timeout, property):
            self._sock_connect_timeout = None
        if isinstance(self.sock_read_timeout, property):
            self._sock_read_timeout = None
        if isinstance(self.connections, property):
            self._connections = 1
        if isinstance(self.connections_per_host, property):
            self._connections_per_host = 0

        self._framework = 'aiohttp'
        self._use_async = True
        self._async_framework = 'asyncio'

    @property
    def total_timeout(self):
        return self._total_timeout
    
    @total_timeout.setter
    def total_timeout(self, value: float | None):
        self._total_timeout = value

    @property
    def connect_timeout(self):
        return self._connect_timeout
    
    @connect_timeout.setter
    def connect_timeout(self, value: float | None):
        self._connect_timeout = value

    @property
    def sock_connect_timeout(self):
        return self._sock_connect_timeout
    
    @sock_connect_timeout.setter
    def sock_connect_timeout(self, value: float | None):
        self._sock_connect_timeout = value

    @property
    def sock_read_timeout(self):
        return self._sock_read_timeout
    
    @sock_read_timeout.setter
    def sock_read_timeout(self, value: float | None):
        self._sock_read_timeout = value

    @property
    def connections(self):
        return self._connections
    
    @connections.setter
    def connections(self, value: int):
        self._connections = value

    @property
    def connections_per_host(self):
        return self._connections_per_host
    
    @connections_per_host.setter
    def connections_per_host(self, value: int):
        self._connections_per_host = value