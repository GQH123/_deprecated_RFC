import inspect
from typing import Any, List
from dataclasses import dataclass, field

from RFC.utils.functional_utils import load_object
from RFC.utils.exception_utils import ParamTypeError, ParamSettingError

from .BaseItemsetConfig import BaseItemsetConfig


@dataclass
class BaseItem():
    name: str = field()
    url: str = field()
    payload: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)
    method: str = field(default='get')


class BaseItemsetIter():
    def __init__(
        self,
        items: List[BaseItem],
    ):
        self.items = iter(items)
        ...

    def __iter__(
        self,
    ):
        return self

    def __next__(
        self,
    ):
        return next(self.items)


class BaseItemset():
    def init_items(
        self,
        items: List[Any] | str,
        preprocess: callable = None,
    ):
        if isinstance(items, str):
            self.items = load_object(items)
        else:
            self.items = items

        if not isinstance(self.items, list):
            raise ParamTypeError('self.items', self.items, list, __name__)

        if preprocess:
            self.items = [preprocess(item) for item in self.items]

    def init_attr(
        self,
        name: str,
        values: List[Any] | callable | None,
    ):
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
        for attr in attrs:
            self.init_attr(attr, attrs[attr])
        if 'name' not in self.attrs:
            self.init_attr('name', lambda i, x: str(i))

    def convert2item(
        self,
    ):
        self.items = [BaseItem(**{k: self.attrs[k][i] for k in self.attrs}) for i, _ in enumerate(self.items)]
        ...

    def __init__(
        self,
        itemset_config: BaseItemsetConfig,
    ):
        self.itemset_config = itemset_config
        self.init_items(itemset_config.items, itemset_config.preprocess)
        self.init_all_attrs(itemset_config.attrs)
        self.convert2item()

    def __iter__(
       self,
    ):
        return BaseItemsetIter(self.items)
        ...

    def __getitem__(
        self,
        idx: int,
    ):
        return self.items[idx]