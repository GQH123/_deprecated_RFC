import os
from dataclasses import dataclass, field

from .RootObject import RootObject
from .functional_utils import get_project_root, save_object, load_object
from .exception_utils import FileNotFoundError, FileFormatError


@dataclass
class BaseModule(RootObject):
    def _to_str(
        self,
        **kwargs,
    ):
        return super()._to_str(base_type=BaseModule, **kwargs)