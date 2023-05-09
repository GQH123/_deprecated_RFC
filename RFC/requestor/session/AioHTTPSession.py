import aiohttp
from typing import List

from RFC.utils.exception_utils import NotSupported

from .Session import Session
from .AioHTTPSessionConfig import AioHTTPSessionConfig


class AioHTTPSession(Session):
    def _init_session_args(
        self,
    ):
        if not self.use_session:
            self.session = None
        else:
            self.connections = self.session_config.connections
            self.connections_per_host = self.session_config.connections_per_host
            self.connector = aiohttp.TCPConnector(
                limit=self.connections,
                limit_per_host=self.connections_per_host,
            )
            self.total_timeout = self.session_config.total_timeout
            self.connect_timeout = self.session_config.connect_timeout
            self.sock_connect_timeout = self.session_config.sock_connect_timeout
            self.sock_read_timeout = self.session_config.sock_read_timeout
            self.timeout = aiohttp.ClientTimeout(
                total=self.total_timeout,
                connect=self.connect_timeout,
                sock_connect=self.sock_connect_timeout,
                sock_read=self.sock_read_timeout,
            )
            self.common_args = ['headers', 'cookies']
            self.session_specific_args = {
                'connector': self.connector,
                'timeout': self.timeout,
            }
            request_args = self.arguments(include=self.common_args)
            request_args.update(self.session_specific_args)
            self.session = aiohttp.ClientSession(
                **request_args
            )

    def _init_request_args(
        self,
    ):
        self.request_specific_args = {}

    def __init__(
        self,
        session_config: AioHTTPSessionConfig,
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
                'get': {
                    'proxies': 'proxy',
                },
                'post': {
                    'proxies': 'proxy',
                    'payload': 'data',
                },
            }
        return super()._request_args(method, excludes, rename_maps, **kwargs)

    async def _request(
        self,
        request_args: dict,
    ):
        if self.session:
            resp = await self.session.request(
                **request_args
            )
        else:
            resp = await aiohttp.request(
                **request_args
            )
        return resp

    async def _request_resp(
        self,
        request_resp,
        rtype: str,  # ['resp', 'text', 'content', 'body', 'json']
    ):
        if rtype == 'resp':
            return request_resp
        elif rtype == 'text':
            return await request_resp.text()
        elif rtype == 'content':
            raise NotSupported('rtype', rtype, ['resp', 'text', 'body', 'json'], __name__)
        elif rtype == 'body':
            return await request_resp.read()
        elif rtype == 'json':
            return await request_resp.json()
        else:
            return super()._request_resp(request_resp, rtype)
    
    def _retrieve_config(
        self,
        return_config: bool = False,
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        my_attr.update({
            'total_timeout': self.total_timeout,
            'connect_timeout': self.connect_timeout,
            'sock_connect_timeout': self.sock_connect_timeout,
            'sock_read_timeout': self.sock_read_timeout,
            'connections': self.connections,
            'connections_per_host': self.connections_per_host,
        })
        if return_config:
            return AioHTTPSessionConfig(**my_attr)
        else:
            return my_attr