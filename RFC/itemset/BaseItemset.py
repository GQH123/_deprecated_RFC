import sys
import random
import inspect
from typing import Any, List, Callable
from dataclasses import dataclass, field

from RFC.utils.BaseModule import BaseModule
from RFC.utils.functional_utils import load_object, log
from RFC.utils.exception_utils import ParamTypeError, ParamSettingError

from .BaseItemsetConfig import BaseItemsetConfig


@dataclass
class BaseItem:
    name: str = field()
    url: str = field()
    payload: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)
    method: str = field(default='get')


class BaseItemset(BaseModule):
    def init_items(
        self,
        items: List[object] | str,
        preprocess: Callable[[object], object] | None = None,
        shuffle: bool = False,
    ):
        if isinstance(items, str):
            self.items = load_object(items)
        else:
            self.items = items

        if not isinstance(self.items, list):
            raise ParamTypeError('self.items', self.items, list, __name__)

        if preprocess:
            self.items = [preprocess(item) for item in self.items]

        if shuffle:
            random.shuffle(self.items)

    def init_attr(
        self,
        name: str,
        values: List[Any] | Callable[[int, object], object] | None,
    ):
        assert isinstance(self.items, list)
        if inspect.isfunction(values):
            attrs = [values(i, item) for i, item in enumerate(self.items)]
        elif isinstance(values, list):
            attrs = values
        else:
            attrs = [values for _ in self.items]
        if len(attrs) != len(self.items):
            raise ParamSettingError(f"Params 'attrs' and 'items' should have the same length, but found {len(attrs)} and {len(self.items)} respectively", __name__, attrs=attrs[:5], items=self.items[:5])
        self.attrs[name] = attrs

    def init_all_attrs(
        self,
        attrs: dict,
    ):
        
        self.attrs = {}
        if 'url' not in attrs:
            raise ParamSettingError("Param 'url' is required", __name__, attrs=attrs)
        if 'method' not in attrs:
            raise ParamSettingError("Param 'method' is required", __name__, attrs=attrs)
        if 'return_type' not in attrs:
            log(f"Param 'return_type' is not set, use ['resp'] instead.", mode='warn', note='Itemset', from_module=__name__)
        if 'name' not in attrs:
            log(f"Param 'name' is not set, use <item_index> instead.", mode='warn', note='Itemset', from_module=__name__)
        for attr in attrs:
            self.init_attr(attr, attrs[attr])
        if 'return_type' not in self.attrs:
            self.init_attr('return_type', [['resp'] for _ in self.items])
        if 'name' not in self.attrs:
            self.init_attr('name', lambda i, x: str(i))
        for i, method in enumerate(self.attrs['method']):
            if method == 'post' and ('payload' not in self.attrs or self.attrs['payload'][i] == {}):
                log(f"Param 'payload' is not set for post item {self.attrs['name'][i]}.", mode='warn', note='Itemset', from_module=__name__)


    def convert2item(
        self,
    ):
        self.items = [BaseItem(**{k: self.attrs[k][i] for k in self.attrs}) for i, _ in enumerate(self.items)]
        ...

    def show(
        self,
        n: int = 10,
    ):
        for item in self.items[:n]:
            log(item, pure_output=True)
        log(pure_output=True)

    def __init__(
        self,
        itemset_config: BaseItemsetConfig,
    ):
        self.itemset_config = itemset_config
        self.name = self.itemset_config.name
        self.init_items(itemset_config.items, itemset_config.preprocess, itemset_config.shuffle)
        self.init_all_attrs(itemset_config.attrs)
        self.convert2item()

    def __iter__(
       self,
    ):
        return iter(self.items)
 
    def __getitem__(
        self,
        idx: int,
    ):
        return self.items[idx]