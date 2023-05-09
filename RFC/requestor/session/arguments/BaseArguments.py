from typing import Any, List
from functools import partial

from RFC.utils.BaseModule import BaseModule
from RFC.utils.functional_utils import check_restriction, parse_restriction
from RFC.utils.structural_utils import import_submodule

from .BaseArgumentsConfig import BaseArgumentsConfig


class BaseArguments(BaseModule):
    def init_all(
        self,
    ):
        self.arguments_partial = None

    def __init__(
        self,
        arguments_config: BaseArgumentsConfig,
    ):
        super().__init__(arguments_config)
        self.config = arguments_config.config.copy()
        self.init_all()

    def _traverse_arguments_config(
        self,
        config: dict,
        module_path: str,
        module_name: str,
        package_name: str,
    ):
        self_params = config['kwargs']
        if 'method' in config:  # this is a leaf
            submodule = import_submodule(module_path+'.'+module_name, package_name)
            return partial(submodule.leaves[config['method']][0], **self_params)
        else:  # this is a branch
            arguments_partial = {}
            for item_name in config:
                if item_name == 'kwargs':
                    continue
                arguments_partial[item_name] = self._traverse_arguments_config(config[item_name], module_path+'.'+item_name, item_name, package_name)
            return arguments_partial

    def _traverse_arguments_partial(
        self,
        arguments_partial: dict,
        url: str | None = None,
        payload: str | None = None,
        **kwargs,
    ):
        arguments = {}
        for argument_name in arguments_partial:
            if isinstance(arguments_partial[argument_name], partial):
                arguments[argument_name] = arguments_partial[argument_name](url=url, payload=payload, **kwargs)
            else:
                arguments[argument_name] = self._traverse_arguments_partial(arguments_partial[argument_name], url=url, payload=payload, **kwargs)
        return arguments

    def _get_arguments_partial(
        self,
    ):
        def arguments_wrapper(arguments_partial, include, exclude, url=None, payload=None, **kwargs):
            arguments = self._traverse_arguments_partial({name: value for name, value in arguments_partial.items() if check_restriction(name, include, exclude)}, url=url, payload=payload, **kwargs)
            return arguments
        self.arguments_partial = partial(arguments_wrapper, self._traverse_arguments_config(self.config, '', '<AnythingIsFine>', '.'.join(__name__.split('.')[:-1])))

    def _get_request_params(
        self,
        url: str | None = None,
        payload: str | None = None,
        include: List[str] | None | str = 'all',
        exclude: List[str] | None | str = 'none',
        rename_map: dict = {},
        **kwargs,
    ):
        include = parse_restriction(include, 'include', __name__)
        exclude = parse_restriction(exclude, 'exclude', __name__)
        if self.arguments_partial is None:
            self._get_arguments_partial()
        arguments = self.arguments_partial(include=include, exclude=exclude, url=url, payload=payload, **kwargs)
        for name in rename_map:
            if name in arguments:
                _argument = arguments.pop(name)
                arguments[rename_map[name]] = _argument
        return arguments

    def __call__(
        self,
        **kwargs,
    ):
        return self._get_request_params(**kwargs)
    
    def _retrieve_config(
        self,
        return_config: bool = False
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        my_attr.update({
            'config': self.config,
        })
        if return_config:
            return BaseArgumentsConfig(**my_attr)
        else:
            return my_attr