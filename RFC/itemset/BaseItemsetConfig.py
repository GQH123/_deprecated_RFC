from typing import List, Any, Callable
from dataclasses import dataclass, field

from RFC.utils.BaseConfig import BaseConfig


@dataclass
class BaseItemsetConfig(BaseConfig):
    items: List[Any] | str
    _items: List[Any] | str = field(init=False, repr=False)

    preprocess: Callable[[object], object]
    _preprocess: Callable[[object], object] = field(init=False, repr=False)

    attrs: dict[str, Callable[[int, object], object]]
    _attrs: dict[str, Callable[[int, object], object]] = field(init=False, repr=False)

    shuffle: bool
    _shuffle: bool = field(init=False, repr=False)

    def __post_init__(self):
        if isinstance(self.items, property):
            self._items = []
        if isinstance(self.preprocess, property):
            self._preprocess = lambda x: x
        if isinstance(self.attrs, property):
            self._attrs = {}
        if isinstance(self.shuffle, property):
            self._shuffle = False
    
    @property
    def items(self):
        return self._items
    
    @items.setter
    def items(self, value: List[Any] | str):
        self._items = value

    @property
    def preprocess(self):
        return self._preprocess
    
    @preprocess.setter
    def preprocess(self, value: Callable[[object], object]):
        self._preprocess = value

    @property
    def attrs(self):
        return self._attrs
    
    @attrs.setter
    def attrs(self, value: dict[str, Callable[[int, object], object]]):
        self._attrs = value

    @property
    def shuffle(self):
        return self._shuffle
    
    @shuffle.setter
    def shuffle(self, value: bool):
        self._shuffle = value