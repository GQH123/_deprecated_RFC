import os
from dataclasses import dataclass, field

from .RootObject import RootObject
from .functional_utils import get_project_root, save_object, load_object
from .exception_utils import FileNotFoundError, FileFormatError


@dataclass
class BaseConfig(RootObject):
    def save(
        self,
        path: str = 'configs',
        savename: str = None,
        mode: str = 'json',
    ):
        if savename is None:
            savename = f'{self._get_self_type_name()}_{self.name}.json'
        path = os.path.join(get_project_root(), path, savename)
        save_object(self.__dict__, path, mode)
    
    def load(
        self,
        path: str = 'configs',
        loadname: str = None,
        mode: str = 'json',
    ):
        if loadname is None:
            loadname = f'{self._get_self_type_name()}_{self.name}.json'
        path = os.path.join(get_project_root(), path, loadname)
        if os.path.exists(path):
            try:
                kwargs = load_object(path, mode)
            except Exception as e:
                raise FileFormatError(path, 'json', __name__)
            self.__call__(**kwargs)
        else:
            raise FileNotFoundError(path, __name__)

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