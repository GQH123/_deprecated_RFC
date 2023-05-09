from typing import List, Any, Callable
from dataclasses import dataclass, field

from RFC.utils.BaseConfig import BaseConfig


@dataclass
class BaseItemsetConfig(BaseConfig):
    items: List[Any] | str = field(default_factory=list)
    preprocess: Callable[[object], object] | None = None
    attrs: dict[str, Callable[[int, object], object]] = field(default_factory=dict)
    shuffle: bool = field(default=False)