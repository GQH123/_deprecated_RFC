from typing import List, Any
from dataclasses import dataclass, field


@dataclass
class BaseItemsetConfig():
    items: List[Any] | str = field()
    preprocess: callable = field()
    attrs: dict = field(default_factory=dict)