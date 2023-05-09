from .BaseItemset import BaseItemset, BaseItem
from .ItemsetConfig import ItemsetConfig


class Item(BaseItem):
    ...


class Itemset(BaseItemset):
    def convert2item(
        self,
    ):
        self.items = [Item(**{k: self.attrs[k][i] for k in self.attrs}) for i, _ in enumerate(self.items)]
        ...
    
    def __init__(
        self,
        itemset_config: ItemsetConfig,
    ):
        super().__init__(itemset_config)