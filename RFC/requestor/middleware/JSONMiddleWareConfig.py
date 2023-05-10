from dataclasses import dataclass, field

from .MiddleWareConfig import MiddleWareConfig


@dataclass
class JSONMiddleWareConfig(MiddleWareConfig):
    ...