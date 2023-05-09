from .BaseRequestor import BaseRequestor
from .RequestorConfig import RequestorConfig


class Requestor(BaseRequestor):
    def __init__(
        self,
        requestor_config: RequestorConfig
    ):
        super().__init__(requestor_config)
        ...
    
    def _retrieve_config(
        self,
        return_config: bool = False
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        ...
        if return_config:
            return RequestorConfig(**my_attr)
        else:
            return my_attr