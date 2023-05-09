import os
from dataclasses import dataclass, field

from .RootObject import RootObject
from .exception_utils import FileNotFoundError, FileFormatError


@dataclass
class BaseModule(RootObject):
    def _to_str(
        self,
        **kwargs,
    ):
        return super()._to_str(base_type=BaseModule, **kwargs)