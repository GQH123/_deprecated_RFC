from dataclasses import dataclass, field

from .SessionConfig import SessionConfig


@dataclass
class AsksSessionConfig(SessionConfig):
    connections: int
    _connections: int = field(init=False, repr=False)

    connection_timeout: int | float | None
    _connection_timeout: int | float | None = field(init=False, repr=False)

    persist_cookies: bool
    _persist_cookies: bool = field(init=False, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.connections, property):
            self._connections = 1
        if isinstance(self.connection_timeout, property):
            self._connection_timeout = 60
        if isinstance(self.persist_cookies, property):
            self._persist_cookies = False
        if isinstance(self.framework, property):
            self._framework = 'asks'
        if isinstance(self.use_async, property):
            self._use_async = True
        if isinstance(self.async_framework, property):
            self._async_framework = 'trio'
    
    @property
    def connections(self):
        return self._connections
    
    @connections.setter
    def connections(self, value: int):
        self._connections = value

    @property
    def connection_timeout(self):
        return self._connection_timeout
    
    @connection_timeout.setter
    def connection_timeout(self, value: int | float | None):
        self._connection_timeout = value

    @property
    def persist_cookies(self):
        return self._persist_cookies
    
    @persist_cookies.setter
    def persist_cookies(self, value: bool):
        self._persist_cookies = value