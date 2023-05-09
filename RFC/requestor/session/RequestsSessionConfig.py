from dataclasses import dataclass, field

from .SessionConfig import SessionConfig


@dataclass
class RequestsSessionConfig(SessionConfig):
    connect_timeout: int | float | None
    _connect_timeout: int | float | None = field(init=False, repr=False)

    read_timeout: int | float | None
    _read_timeout: int | float | None = field(init=False, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.connect_timeout, property):
            self._connect_timeout = None
        if isinstance(self.read_timeout, property):
            self._read_timeout = None
        if isinstance(self.framework, property):
            self._framework = 'requests'
        if isinstance(self.use_async, property):
            self._use_async = False

    @property
    def connect_timeout(self):
        return self._connect_timeout
    
    @connect_timeout.setter
    def connect_timeout(self, value: int | float | None):
        self._connect_timeout = value

    @property
    def read_timeout(self):
        return self._read_timeout
    
    @read_timeout.setter
    def read_timeout(self, value: int | float | None):
        self._read_timeout = value