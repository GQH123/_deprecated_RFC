from typing import List

from RFC.itemset.RawItemset import RawItem
from RFC.utils.exception_utils import ConditionOverflowError, NotSupportedError

from .headers.headers import get_headers
from .BaseSessionConfig import BaseSessionConfig


class BaseSession():
    def _init_headers(self):
        self.headers_type = self.session_config.headers_type
        self.headers_config = self.session_config.headers_config
        self.headers = get_headers(self.headers_type, self.headers_config)

    def _init_session(
        self,
    ):
        if not self.use_session:
            self.session = None
        else:
            request_params = self.headers()
            request_params
            self.session = ...
        ...

    def _init_states(
        self,
    ):
        self.contiguous_failed_counts = 0
        if self.session_config.contiguous_failed_counts_threshold:
            self.contiguous_failed_counts_threshold = self.session_config.contiguous_failed_counts_threshold
        else:
            self.session_config.contiguous_failed_counts_threshold = -1

    def __init__(
        self,
        session_config: BaseSessionConfig,
        use_session: bool,
    ):
        self.session_config = session_config
        self.use_session = use_session

        self._init_headers()
        self._init_session()
        self._init_states()

    def _parse_request_params(
        self,
        item: RawItem,
    ):
        all_supported_methods = ['get', 'post']
        if item.method not in all_supported_methods:
            raise NotSupportedError(item.method, all_supported_methods)
        if item.method == 'get':
            request_params = self.headers(item.url)
        elif item.method == 'post':
            request_params = self.headers(item.url, item.payload)
        else:
            raise ConditionOverflowError(item.method)
        return request_params

    def _session_request(
        self,
        request_params: dict,
    ):
        if self.session:
            resp = ...
        else:
            resp = ...
        return resp
        ...

    def _get_returned_request_resp(
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
            return request_resp.json
        else:
            raise ConditionOverflowError(rtype)
        ...

    def _return_response(
        self,
        request_resp,
        return_type: List[str],
    ):
        all_supported_rtype = ['resp', 'text', 'content', 'body', 'json']
        results = {}
        for rtype in return_type:
            if rtype not in all_supported_rtype:
                raise NotSupportedError(rtype, all_supported_rtype)
            if rtype in results:
                continue
            results[rtype] = self._get_returned_request_resp(request_resp, rtype)
        return results

    def request(
        self,
        item: RawItem,
        return_type: str,
    ):
        if not isinstance(return_type, list):
            return_type = [return_type]
        request_params = self._parse_request_params(item, self.headers)
        request_resp = self._session_request(request_params)
        request_results = self._return_response(request_resp, return_type)
        return request_results

    def _check_session_renew(
        self,
    ):
        if self.contiguous_failed_counts == self.contiguous_failed_counts_threshold:
            self.contiguous_failed_counts = 0
            return True
        return False