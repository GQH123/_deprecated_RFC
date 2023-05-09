import asks
from typing import List

from .Session import Session
from .AsksSessionConfig import AsksSessionConfig


class AsksSession(Session):
    def _init_session_args(
        self,
        session_config: AsksSessionConfig,
    ):
        if not self.use_session:
            self.session = None
        else:
            self.connections = session_config.connections
            self.persist_cookies = session_config.persist_cookies
            self.common_args = ['headers']
            self.session_specific_args = {
                'connections': self.connections,
                'persist_cookies': self.persist_cookies,
            }
            request_args = self.arguments(include=self.common_args)
            request_args.update(self.session_specific_args)
            self.session = asks.Session(
                **request_args
            )

    def _init_request_args(
        self,
        session_config: AsksSessionConfig,
    ):
        self.request_specific_args = {
            'timeout': session_config.request_timeout,
            'connection_timeout': session_config.connection_timeout,
        }

    def __init__(
        self,
        session_config: AsksSessionConfig,
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
                'get': [
                    'proxies',
                    'payload',
                ],
                'post': [
                    'proxies',
                ],
            }
        if rename_maps is None:
            rename_maps = {
                'get': {},
                'post': {
                    'payload': 'data',
                },
            }
        return super()._request_args(method, excludes, rename_maps, **kwargs)

    async def _request(
        self,
        request_args: dict,
    ):
        if self.use_session:
            resp = await self.session.request(
                **request_args
            )
        else:
            resp = await asks.request(
                **request_args
            )
        return resp

    """
    async def _request_resp(
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
            return request_resp.body
        elif rtype == 'json':
            return request_resp.json()
        else:
            return super()._request_resp(request_resp, rtype)
    """
    
    def _retrieve_config(
        self,
        return_config: bool = False,
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        my_attr.update({
            'connections': self.connections,
            'connect_timeout': self.connect_timeout,
            'persist_cookies': self.persist_cookies,
        })
        if return_config:
            return AsksSessionConfig(**my_attr)
        else:
            return my_attr