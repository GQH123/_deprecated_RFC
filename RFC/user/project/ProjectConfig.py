from dataclasses import dataclass, field

from RFC.utils.functional_utils import load_object

from .BaseProjectConfig import BaseProjectConfig


@dataclass
class ProjectConfig(BaseProjectConfig):
    def __init__(
        self,
        config_path: str = None,
        **kwargs,
    ):
        if config_path:
            config = load_object(config_path)
            kwargs.update(config)
        super().__init__(**kwargs)