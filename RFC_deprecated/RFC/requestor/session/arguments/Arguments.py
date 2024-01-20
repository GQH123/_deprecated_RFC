from .ArgumentsConfig import ArgumentsConfig
from .BaseArguments import BaseArguments


class Arguments(BaseArguments):
    def __init__(
        self,
        arguments_config: ArgumentsConfig,
    ):
        super().__init__(arguments_config)
    
    def _retrieve_config(
        self,
        return_config: bool = False
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        ...
        if return_config:
            return ArgumentsConfig(**my_attr)
        else:
            return my_attr