from .ArgumentsConfig import ArgumentsConfig
from .BaseArguments import BaseArguments


class Arguments(BaseArguments):
    def __init__(
        self,
        arguments_config: ArgumentsConfig,
    ):
        super().__init__(arguments_config)