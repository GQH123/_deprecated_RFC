from .ProjectConfig import ProjectConfig
from .BaseProject import BaseProject


class Project(BaseProject):
    def __init__(
        self,
        project_config: ProjectConfig,
    ):
        super().__init__(project_config)
        ...

    def _retrieve_config(
        self,
        return_config: bool = False
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        ...
        if return_config:
            return ProjectConfig(**my_attr)
        else:
            return my_attr