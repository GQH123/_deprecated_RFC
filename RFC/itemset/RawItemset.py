from typing import List
from dataclasses import dataclass, field

from .Itemset import Itemset, Item
from .RawItemsetConfig import RawItemsetConfig


@dataclass
class RawItem(Item):
    ...


class RawItemset(Itemset):
    def convert2item(
        self,
    ):
        self.items = [RawItem(**{k: self.attrs[k][i] for k in self.attrs}) for i, _ in enumerate(self.items)]
        ...

    def __init__(
        self,
        itemset_config: RawItemsetConfig,
    ):
        super().__init__(itemset_config)