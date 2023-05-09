from typing import List
from functools import partial

from RFC.itemset.RawItemset import RawItem
from RFC.utils.BaseModule import BaseModule
from RFC.utils.exception_utils import ConditionOverflowError, ParamValueError

from .arguments.arguments import get_arguments
from .BaseSessionConfig import BaseSessionConfig


class BaseSession(BaseModule):
    def _init_arguments(
        self,
        session_config: BaseSessionConfig,
    ):
        self.arguments_config = session_config.arguments_config
        self.arguments = get_arguments(self.arguments_config)

    def _init_attrs(
        self,
        session_config: BaseSessionConfig,
    ):
        self.use_async = session_config.use_async
        self.framework = session_config.framework
        self.async_framework = session_config.async_framework
        self.use_session = session_config.use_session

    def _init_session_args(
        self,
        session_config: BaseSessionConfig,
    ):
        self.session = ...
        ...

    def _init_request_args(
        self,
        session_config: BaseSessionConfig,
    ):
        ...

    def _init_states(
        self,
        session_config: BaseSessionConfig,
    ):
        self.method_request_args = {}
        self.contiguous_failed_counts = 0
        if session_config.contiguous_failed_counts_threshold:
            self.contiguous_failed_counts_threshold = session_config.contiguous_failed_counts_threshold
        else:
            self.contiguous_failed_counts_threshold = -1

    def _init_all(
        self,
        session_config: BaseSessionConfig,
    ):
        self._init_arguments(session_config=session_config)
        self._init_attrs(session_config=session_config)
        self._init_session_args(session_config=session_config)
        self._init_request_args(session_config=session_config)
        self._init_states(session_config=session_config)

    def __init__(
        self,
        session_config: BaseSessionConfig,
    ):
        super().__init__(session_config)
        self._init_all(session_config=session_config)

    def _request_args(
        self,
        method: str,
        excludes: dict[str, List[str]],
        rename_maps: dict[str, dict[str, str]],
        **kwargs,
    ):
        if method in self.method_request_args:
            return self.method_request_args[method]

        exclude = excludes[method]
        rename_map = rename_maps[method]
        if self.use_session:
            exclude += self.common_args
        kwargs = {k: v[method] for k, v in kwargs.items() if method in v}
        request_args = partial(
            self.arguments,
            exclude=exclude,
            rename_map=rename_map,
            **kwargs,
        )
        self.method_request_args[method] = request_args
        return request_args

    def _request(
        self,
        request_args: dict,
    ):
        ...

    async def _session_request(
        self,
        item: RawItem,
        rank: int,
    ):
        all_supported_methods = ['get', 'post']
        if item.method not in all_supported_methods:
            raise ParamValueError('item.method', item.method, all_supported_methods, __name__)

        if item.method == 'get':
            request_args = self._request_args('get')(
                url=item.url,
                params=item.params,
                rank=rank,
            )
        elif item.method == 'post':
            request_args = self._request_args('post')(
                url=item.url,
                params=item.params,
                payload=item.payload,
                rank=rank,
            )
        else:
            raise ConditionOverflowError(item.method, __name__)

        if self.use_session:
            request_args.update(self.request_specific_args)
        else:
            request_args.update(self.request_specific_args)
            request_args.update(self.arguments(include=self.common_args))
        request_args.update(dict(
            method=item.method,
        ))
        if self.use_async:
            resp = await self._request(request_args)
        else:
            resp = self._request(request_args)
        return resp

    async def request(
        self,
        item: RawItem,
        rank: int,
    ):
        request_resp = await self._session_request(item, rank)
        return request_resp

    def _check_session_renew(
        self,
    ):
        if self.contiguous_failed_counts == self.contiguous_failed_counts_threshold:
            self.contiguous_failed_counts = 0
            return True
        return False

    async def _close(
        self,
    ):
        ...

    def _retrieve_config(
        self,
        return_config: bool = False,
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        my_attr.update({
            'arguments_config': self.arguments.__config__(),
            'contiguous_failed_counts_threshold': self.contiguous_failed_counts_threshold,
            'use_session': self.use_session,
            'framework': self.framework,
            'use_async': self.use_async,
            'async_framework': self.async_framework,
        })
        if return_config:
            return BaseSessionConfig(**my_attr)
        else:
            return my_attr