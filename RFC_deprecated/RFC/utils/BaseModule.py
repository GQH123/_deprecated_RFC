import os
from dataclasses import dataclass, field

from .RootObject import RootObject
from .BaseConfig import BaseConfig
from .exception_utils import FileNotFoundError, FileFormatError
from .functional_utils import save_object


class BaseModule(RootObject):
    def __init__(
        self, 
        config: BaseConfig,
    ):
        self.name = config.name

    def _to_str(
        self,
        **kwargs,
    ):
        return super()._to_str(base_type=BaseModule, **kwargs)
    
    def _retrieve_config(
        self,
        return_config: bool = False,  # return Config if True, else return attr(dict)
    ):
        my_attr = {
            'name': self.name
        }
        if not return_config:
            return my_attr
        else:
            return BaseConfig(**my_attr)

    def __config__(
        self,
    ):
        return self._retrieve_config(return_config=True)
    
    def save_config(
        self,
    ):
        self.__config__().save(self.name)