from collections import OrderedDict

from .attr import get_attr_shadowed_name


__all__ = [
    'AttrDict',
    'FrozenDict',
    'FrozenAttrDict',
]


class AttrDict(dict):
    """
        A dict whose keys can be accessed as attributes.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            setattr(self, key, value)


class FrozenDict(OrderedDict):
    """
        A dict that cannot be modified after initialization.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            setattr(self, key, value)
        self.__frozen = True

    def __delitem__(self, *args, **kwargs):
        raise Exception(f"You cannot use ``__delitem__`` on a {self.__class__.__name__} instance.")

    def setdefault(self, *args, **kwargs):
        raise Exception(f"You cannot use ``setdefault`` on a {self.__class__.__name__} instance.")

    def pop(self, *args, **kwargs):
        raise Exception(f"You cannot use ``pop`` on a {self.__class__.__name__} instance.")

    def update(self, *args, **kwargs):
        raise Exception(f"You cannot use ``update`` on a {self.__class__.__name__} instance.")

    def __setattr__(self, name, value):
        if hasattr(self, get_attr_shadowed_name(self, '__frozen')) and self.__frozen:
            raise Exception(f"You cannot use ``__setattr__`` on a {self.__class__.__name__} instance.")
        super().__setattr__(name, value)

    def __setitem__(self, name, value):
        if hasattr(self, get_attr_shadowed_name(self, '__frozen')) and self.__frozen:
            raise Exception(f"You cannot use ``__setattr__`` on a {self.__class__.__name__} instance.")
        super().__setitem__(name, value)
        
    def __getitem__(self, name):
        return super().__getitem__(name)
    
    
class FrozenAttrDict(FrozenDict, AttrDict):
    """
        A dict whose keys can be accessed as attributes and cannot be modified after initialization.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self