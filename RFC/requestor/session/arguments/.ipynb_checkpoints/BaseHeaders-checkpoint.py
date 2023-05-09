from typing import Any, List
from functools import partial

from .BaseHeadersConfig import BaseHeadersConfig
from RFC.utils.exception_utils import NotSupportedError
from RFC.utils.structural_utils import parse_restriction, check_restriction, import_submodule


class BaseHeaders:
    def init_all(
        self,
    ):
        self.headers_partial = None
        self.include = self.headers_config['kwargs'].get('include', 'all')
        self.exclude = self.headers_config['kwargs'].get('exclude', 'none')

    def __init__(
        self,
        headers_config: BaseHeadersConfig,
    ):
        self.headers_config = headers_config
        self.init_all()

    def _get_headers_partial(
        self,
    ):
        def wrapper(headers_partial, **kwargs):
            headers = {}
            for header_name in headers_partial:
                headers[header_name] = headers_partial[header_name](**kwargs)
            return headers

        include = parse_restriction(self.include, 'include', __name__)
        exclude = parse_restriction(self.exclude, 'exclude', __name__)
        headers_partial = {}
        for header_name in self.headers_config:
            if header_name == 'kwargs' or not check_restriction(header_name, include, exclude):
                continue
            submodule = import_submodule(header_name, __name__)
            headers_partial[header_name] = partial(submodule.leaves[self.headers_config[header_name]['method']], **self.headers_config[header_name]['params'])
        return partial(wrapper, headers_partial)

    def _get_request_params(
        self,
        url: str | None = None,
        include: List[str] | None | str = 'all',
        exclude: List[str] | None | str = 'none',
        **kwargs,
    ):
        include = parse_restriction(include, 'include', __name__)
        exclude = parse_restriction(exclude, 'exclude', __name__)
        if self.headers_partial is None:
            self.headers_partial = self._get_headers_partial()
        headers = {name: value for name, value in self.headers_partial(url, **kwargs).items() if check_restriction(name, include, exclude)}
        cookies = headers.pop('cookies', None)
        proxies = headers.pop('proxies', None)
        url = headers.pop('url', None)
        payload = headers.pop('payload', None)
        base = headers.pop('base', {})
        base.update(headers)
        headers = base

        request_params = {}
        request_params['headers'] = headers
        if url:
            request_params['url'] = url
        if cookies:
            request_params['cookies'] = cookies
        if proxies:
            request_params['proxies'] = proxies
        if payload:
            request_params['payload'] = payload
        return request_params

    def __call__(
        self,
        **kwargs,
    ):
        return self._get_request_params(**kwargs)

    def __setattr__(
        self,
        name: str,
        value: Any,
    ):
        all_supported_names = [
            'include',
            'exclude',
            'headers_config',
        ]
        if name not in all_supported_names:
            raise NotSupportedError(name, all_supported_names, __name__)
        else:
            super().__setattr__(name, value)
            self.init_all()

    def __getattr__(
        self,
        name: str,
    ):
        all_supported_names = [
            'include',
            'exclude',
            'headers_config',
        ]
        if name not in all_supported_names:
            raise NotSupportedError(name, all_supported_names, __name__)
        else:
            return super().__getattr__(name)