from typing import Any

from RFC.itemset.RawItemset import RawItemset, RawItem
from RFC.utils.exception_utils import NotSupportedError

from .session.session import get_session
from .BaseRequestorConfig import BaseRequestorConfig


class BaseRequestor():
    def _init_session(self):
        self.session = get_session(self.framework, self.session_config, self.use_session)

    def _init_framework(self):
        sync_frameworks = ['requests']
        async_frameworks = ['asks', 'aiohttp']
        if self.framework in sync_frameworks:
            self.use_async = False
        elif self.framework in async_frameworks:
            self.use_async = True
        else:
            raise NotSupportedError(self.framework, sync_frameworks+async_frameworks, __name__)

    def _init_all(self):
        self.framework = self.requestor_config.framework
        self.session_config = self.requestor_config.session_config
        self.use_session = self.requestor_config.use_session
        self._init_framework()
        self._init_session()

    def __init__(
        self,
        requestor_config: BaseRequestorConfig
    ):
        self.requestor_config = requestor_config
        self._init_all()

    def _fetch(
        self,
        item: RawItem,
        return_type: str = 'resp',  # ['resp', 'text', 'content', 'raw', 'json']
    ):
        return self.session.request(item, return_type)

    def __call__(
        self,
        items: RawItemset,
        method: str = 'get',
        return_type: str = 'resp',  # ['resp', 'text', 'content', 'raw', 'json']
        return_dict: bool = False,
    ):
        if not isinstance(items, list):
            items = [items]
        results = [] if not return_dict else {}
        for item in items:
            result = self._fetch(item, method=method, return_type=return_type)
            if return_dict:
                results[item.name] = result
            else:
                results.append(result)
        return results