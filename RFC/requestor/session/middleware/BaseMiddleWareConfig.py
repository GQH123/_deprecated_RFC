from dataclasses import dataclass, field

from RFC.utils.BaseConfig import BaseConfig


@dataclass
class BaseMiddleWareConfig(BaseConfig):
    framework: str