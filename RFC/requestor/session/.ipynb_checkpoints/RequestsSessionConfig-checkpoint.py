from dataclasses import dataclass, field

from .SessionConfig import SessionConfig


@dataclass
class RequestsSessionConfig(SessionConfig):
    ...