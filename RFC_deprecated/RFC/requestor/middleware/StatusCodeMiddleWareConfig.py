from dataclasses import dataclass, field

from .MiddleWareConfig import MiddleWareConfig


@dataclass
class StatusCodeMiddleWareConfig(MiddleWareConfig):
    expected_status_codes: list[int] | int
    _expected_status_codes: list[int] | int = field(init=False, repr=False)

    strict: bool
    _strict: bool = field(init=False, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.expected_status_codes, property):
            self._expected_status_codes = [200]
        if isinstance(self.strict, property):
            self._strict = False
    
    @property
    def expected_status_codes(self):
        return self._expected_status_codes
    
    @expected_status_codes.setter
    def expected_status_codes(self, value: list[int] | int):
        if not isinstance(value, list) and not isinstance(value, property):
            value = [value]
        self._expected_status_codes = value
    
    @property
    def strict(self):
        return self._strict
    
    @strict.setter
    def strict(self, value: bool):
        self._strict = value