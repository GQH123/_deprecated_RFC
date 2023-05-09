from dataclasses import dataclass, field

from RFC.utils.functional_utils import BaseConfig

from .headers.BaseHeadersConfig import BaseHeadersConfig


@dataclass
class BaseSessionConfig(BaseConfig):
    headers: BaseHeadersConfig = field(default_factory=BaseHeadersConfig)
    headers_type: str = field(default='default')