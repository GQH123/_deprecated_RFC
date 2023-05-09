from dataclasses import dataclass, field

from .BaseSessionConfig import BaseSessionConfig


@dataclass
class SessionConfig(BaseSessionConfig):
    framework: str = field(default='<unknown>')
    use_async: bool = field(default=False)
    async_framework: str | None = field(default=None)