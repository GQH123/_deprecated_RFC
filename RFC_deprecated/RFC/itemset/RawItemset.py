from .Itemset import Itemset, Item
from .RawItemsetConfig import RawItemsetConfig


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
        ...

    def _retrieve_config(
        self,
        return_config: bool = False
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        ...
        if return_config:
            return RawItemsetConfig(**my_attr)
        else:
            return my_attr