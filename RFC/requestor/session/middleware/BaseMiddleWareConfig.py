from dataclasses import dataclass, field

from RFC.utils.BaseConfig import BaseConfig


@dataclass
class BaseMiddleWareConfig(BaseConfig):
    framework: str
    _framework: str = field(init=False, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.framework, property):
            self._framework = None

    @property
    def framework(self):
        return self._framework
    
    @framework.setter
    def framework(self, value: str):
        self._framework = value