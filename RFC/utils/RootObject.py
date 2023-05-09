import os
from dataclasses import dataclass, field

from .functional_utils import log, parse_restriction, check_restriction, pretty_print_parser


@dataclass
class RootObject:
    name: str
    _name: str = field(init=False, repr=False)

    def __post_init__(self):
        if isinstance(self.name, property):
            self._name = '<anonymous>'
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value: str):
        self._name = value

    def print(
        self,
        include='all',
        exclude='none',
        include_sub=True,
        **kwargs,
    ):
        log('\n'+self._to_str(include=include, exclude=exclude, include_sub=include_sub), file='stdout', mode='info', **kwargs)

    def _get_self_type_name(
        self,
    ):
        return type(self).__name__
    
    def _to_str(
        self,
        include='all',
        exclude='none',
        include_sub=True,
        base_type=object,
    ):
        include = parse_restriction(include, 'include', __name__)
        exclude = parse_restriction(exclude, 'exclude', __name__)
        _dict = {}
        for k, v in self.__dict__.items():
            if not include_sub and isinstance(v, base_type):
                continue
            if check_restriction(k, include, exclude):
                _dict[k] = v
        return f"{self._get_self_type_name()}\n" + pretty_print_parser(_dict)

    def __str__(
        self,
    ):
        # return f"{self._get_self_type_name()}\n" + pretty_print_parser(self.__dict__)
        return self._to_str()