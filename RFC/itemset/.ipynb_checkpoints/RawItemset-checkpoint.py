from typing import List
from dataclasses import dataclass, field

from .Itemset import Itemset, Item, ItemsetIter


@dataclass
class RawItem(Item):
    ...


class RawItemsetIter(ItemsetIter):
    def __init__(
        self,
        items: List[RawItem],
    ):
        super().__init__(items)
        ...


class RawItemset(Itemset):
    def convert2item(
        self,
    ):
        self.items = [RawItem(**{k: self.attrs[k][i] for k in self.attrs}) for i, _ in enumerate(self.items)]
        ...

    def __iter__(
       self,
    ):
        return RawItemsetIter(self.items)
        ...