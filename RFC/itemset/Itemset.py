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
        ...
    
    def _retrieve_config(
        self,
        return_config: bool = False
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        ...
        if return_config:
            return ItemsetConfig(**my_attr)
        else:
            return my_attr