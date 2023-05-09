from typing import List
from dataclasses import dataclass, field

from .BaseItemset import BaseItemset, BaseItem, BaseItemsetIter


@dataclass
class Item(BaseItem):
    ...


class ItemsetIter(BaseItemsetIter):
    def __init__(
        self,
        items: List[Item],
    ):
        super().__init__(items)
        ...


class Itemset(BaseItemset):
    def convert2item(
        self,
    ):
        self.items = [Item(**{k: self.attrs[k][i] for k in self.attrs}) for i, _ in enumerate(self.items)]
        ...

    def __iter__(
       self,
    ):
        return ItemsetIter(self.items)
        ...