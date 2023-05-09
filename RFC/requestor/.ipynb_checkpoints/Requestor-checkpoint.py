from .BaseRequestor import BaseRequestor
from .RequestorConfig import RequestorConfig


class Requestor(BaseRequestor):
    def __init__(
        self,
        requestor_config: RequestorConfig
    ):
        super().__init__(requestor_config)