from dataclasses import dataclass, field

from .MiddleWareConfig import MiddleWareConfig


@dataclass
class JSON_MiddleWareConfig(MiddleWareConfig):
    savename: callable
    _savename: callable = field(init=False, repr=False)

    mode: str
    _mode: str = field(init=False, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.savename, property):
            self._savename = lambda item: f'{item.name}.json'
        if isinstance(self.mode, property):
            self._mode = 'json'
    
    @property
    def savename(self):
        return self._savename
    
    @savename.setter
    def savename(self, value: callable):
        self._savename = value

    @property
    def mode(self):
        return self._mode
    
    @mode.setter
    def mode(self, value: str):
        self._mode = value