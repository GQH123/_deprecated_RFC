from dataclasses import dataclass, field

from .BaseSessionConfig import BaseSessionConfig


@dataclass
class SessionConfig(BaseSessionConfig):
    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.framework, property):
            self._framework = '<unknown>'
        if isinstance(self.use_async, property):
            self._use_async = False
        if isinstance(self.async_framework, property):
            self._async_framework = None