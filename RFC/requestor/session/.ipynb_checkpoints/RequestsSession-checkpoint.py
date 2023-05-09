import requests

from RFC.itemset.RawItemset import RawItem

from .Session import Session
from .RequestsSessionConfig import RequestsSessionConfig


class RequestsSession(Session):
    def _init_session(
        self,
    ):
        if not self.use_session:
            self.session = None
        else:
            params = {}
            if self.session_config.headers:
                params['headers'] = self.session_config.headers
            if self.session_config.cookies:
                params['cookies'] = self.session_config.cookies
            self.session = requests.Session(**params)

    def __init__(
        self,
        session_config: RequestsSessionConfig,
        use_session: bool,
    ):
        super().__init__(session_config, use_session)

    def _session_request(
        self,
        item: RawItem,
        request_params: dict,
    ):
        if self.session:
            resp = self.session.request(item.method, **request_params)
        else:
            resp = requests.request(item.method, **request_params)
        return resp

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
            return request_resp.raw.read()
        elif rtype == 'json':
            return request_resp.json()
        else:
            return super()._get_returned_request_resp(request_resp, rtype)