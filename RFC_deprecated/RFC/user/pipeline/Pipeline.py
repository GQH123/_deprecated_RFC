from .BasePipeline import BasePipeline
from .PipelineConfig import PipelineConfig


class Pipeline(BasePipeline):
    def __init__(
        self,
        pipeline_config: PipelineConfig,
    ):
        super().__init__(pipeline_config)
        ...

    def _retrieve_config(
        self,
        return_config: bool = False
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        ...
        if return_config:
            return PipelineConfig(**my_attr)
        else:
            return my_attr