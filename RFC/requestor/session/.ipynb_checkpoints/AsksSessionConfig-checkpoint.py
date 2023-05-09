from dataclasses import dataclass, field

from .SessionConfig import SessionConfig


@dataclass
class AsksSessionConfig(SessionConfig):
    connections: int = field(default=1)
    persist_cookies: bool = field(default=False)