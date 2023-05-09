import requests
from typing import List

from .Session import Session
from .RequestsSessionConfig import RequestsSessionConfig


class RequestsSession(Session):
    def _init_session_args(
        self,
        session_config: RequestsSessionConfig,
    ):
        if not self.use_session:
            self.session = None
        else:
            self.common_args = ['cookies', 'proxies', 'headers']
            self.session_specific_args = {}
            request_args = self.arguments(include=self.common_args)
            request_args.update(self.session_specific_args)
            self.session = requests.Session(
                **request_args
            )

    def _init_request_args(
        self,
        session_config: RequestsSessionConfig,
    ):
        self.connect_timeout = session_config.connect_timeout
        self.read_timeout = session_config.read_timeout
        if self.connect_timeout is not None and self.read_timeout is not None:
            self.timeout = (self.connect_timeout, self.read_timeout)
        else:
            self.timeout = None
        self.request_specific_args = {
            'timeout': self.timeout,
        }

    def __init__(
        self,
        session_config: RequestsSessionConfig,
    ):
        super().__init__(session_config)

    def _request_args(
        self,
        method: str,
        excludes: dict[str, List[str]] = None,
        rename_maps: dict[str, dict[str, str]] = None,
        **kwargs,
    ):
        if excludes is None:
            excludes = {
                'get': ['payload'],
                'post': [],
            }
        if rename_maps is None:
            rename_maps = {
                'get': {},
                'post': {
                    'payload': 'data',
                },
            }
        return super()._request_args(method, excludes, rename_maps, **kwargs)

    def _request(
        self,
        request_args: dict,
    ):
        if self.session:
            resp = self.session.request(
                **request_args
            )
        else:
            resp = requests.request(
                **request_args
            )
        return resp

    def _request_resp(
        self,
        request_resp,
        rtype: str,  # ['resp', 'text', 'content', 'body', 'json']
    ):
        if rtype == 'resp':
            return request_resp
        elif rtype == 'text':
            return request_resp.text
        elif rtype == 'content':
            return request_resp.content
        elif rtype == 'body':
            return request_resp.raw.read()
        elif rtype == 'json':
            return request_resp.json()
        else:
            return super()._get_returned_request_resp(request_resp, rtype)

    def _retrieve_config(
        self,
        return_config: bool = False,
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        my_attr.update({
            'connect_timeout': self.connect_timeout,
            'read_timeout': self.read_timeout,
        })
        if return_config:
            return RequestsSessionConfig(**my_attr)
        else:
            return my_attr