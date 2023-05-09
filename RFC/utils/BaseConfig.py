import os
from dataclasses import dataclass, field

from .RootObject import RootObject
from .functional_utils import save_object, load_object
from .exception_utils import FileNotFoundError, FileFormatError


@dataclass
class BaseConfig(RootObject):
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
        self.__dict__.update(kwargs)
        return self