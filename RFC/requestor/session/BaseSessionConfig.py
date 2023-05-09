from dataclasses import dataclass, field

from RFC.utils.BaseConfig import BaseConfig

from .arguments.ArgumentsConfig import ArgumentsConfig


@dataclass
class BaseSessionConfig(BaseConfig):
    arguments_config: ArgumentsConfig
    _arguments_config: ArgumentsConfig = field(init=False, repr=False)

    contiguous_failed_counts_threshold: int | None
    _contiguous_failed_counts_threshold: int | None = field(init=False, repr=False)

    use_session: bool
    _use_session: bool = field(init=False, repr=False)

    framework: str
    _framework: str = field(init=False, repr=False)

    use_async: bool
    _use_async: bool = field(init=False, repr=False)

    async_framework: str | None
    _async_framework: str | None = field(init=False, repr=False)

    def __post_init__(self):
        if isinstance(self.arguments_config, property):
            self._arguments_config = ArgumentsConfig()
        if isinstance(self.contiguous_failed_counts_threshold, property):
            self._contiguous_failed_counts_threshold = None
        if isinstance(self.use_session, property):
            self._use_session = True
        if isinstance(self.framework, property):
            self._framework = '<unknown>'
        if isinstance(self.use_async, property):
            self._use_async = False
        if isinstance(self.async_framework, property):
            self._async_framework = None
    
    @property
    def arguments_config(self):
        return self._arguments_config
    
    @arguments_config.setter
    def arguments_config(self, value: ArgumentsConfig):
        self._arguments_config = value

    @property
    def contiguous_failed_counts_threshold(self):
        return self._contiguous_failed_counts_threshold
    
    @contiguous_failed_counts_threshold.setter
    def contiguous_failed_counts_threshold(self, value: int | None):
        self._contiguous_failed_counts_threshold = value

    @property
    def use_session(self):
        return self._use_session
    
    @use_session.setter
    def use_session(self, value: bool):
        self._use_session = value

    @property
    def framework(self):
        return self._framework
    
    @framework.setter
    def framework(self, value: str):
        self._framework = value

    @property
    def use_async(self):
        return self._use_async
    
    @use_async.setter
    def use_async(self, value: bool):
        self._use_async = value

    @property
    def async_framework(self):
        return self._async_framework
    
    @async_framework.setter
    def async_framework(self, value: str | None):
        self._async_framework = value