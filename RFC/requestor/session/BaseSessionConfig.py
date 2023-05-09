from dataclasses import dataclass, field

from RFC.utils.BaseConfig import BaseConfig

from .arguments.ArgumentsConfig import ArgumentsConfig


@dataclass
class BaseSessionConfig(BaseConfig):
    arguments_config: ArgumentsConfig = field(default_factory=ArgumentsConfig)
    contiguous_failed_counts_threshold: int | None = field(default=None)
    use_session: bool = field(default=True)
    framework: str = field(default='<unknown>')
    use_async: bool = field(default=False)
    async_framework: str | None = field(default=None)