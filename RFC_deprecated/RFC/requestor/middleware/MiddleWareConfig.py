from dataclasses import dataclass, field

from .BaseMiddleWareConfig import BaseMiddleWareConfig


@dataclass
class MiddleWareConfig(BaseMiddleWareConfig):
    ...

    """ example
    expected_error_codes: list[int]
    _expected_error_codes: list[int] = field(init=False, repr=False)

    def __post_init__(self):
        super().__post_init__()  # remember to call super().__post_init__()
        if isinstance(self.expected_error_codes, property):
            self.expected_error_codes = [200]
    
    @property
    def expected_error_codes(self):
        return self._expected_error_codes
    
    @expected_error_codes.setter
    def expected_error_codes(self, value):
        self._expected_error_codes = value
    """