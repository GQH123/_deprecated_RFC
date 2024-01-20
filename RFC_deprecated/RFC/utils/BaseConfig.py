import os
from dataclasses import dataclass, field

from .RootObject import RootObject
from .functional_utils import save_object, load_object


@dataclass
class BaseConfig(RootObject):
    name: str
    _name: str = field(init=False, repr=False)

    def __post_init__(self):
        if isinstance(self.name, property):
            self.name = '<anonymous>'
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value: str):
        self._name = value

    def save(
        self,
        savename: str = None,
        mode: str = 'json',
    ):
        if savename is None:
            savename = f'{self._get_self_type_name()}_{self.name}.json'
        save_object(self.__dict__, savename, 'config', mode)
    
    def load(
        self,
        loadname: str = None,
        mode: str = 'json',
    ):
        if loadname is None:
            loadname = f'{self._get_self_type_name()}_{self.name}.json'
        kwargs = load_object(loadname, mode, 'config')
        self.__call__(**kwargs)

    def _to_str(
        self,
        **kwargs,
    ):
        return super()._to_str(base_type=BaseConfig, **kwargs)

    def __call__(
        self,
        **kwargs,
    ):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise AttributeError(f'No attribute named {k} in {self._get_self_type_name()}')
        return self