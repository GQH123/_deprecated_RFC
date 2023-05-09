from RFC.utils.exception_utils import ConditionOverflowError

from .BaseSession import BaseSession
from .SessionConfig import SessionConfig


class Session(BaseSession):
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
            self.session = ...
        ...

    def __init__(
        self,
        session_config: SessionConfig,
        use_session: bool,
    ):
        super().__init__(session_config, use_session)

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
            return super()._get_returned_request_resp(request_resp, rtype)
        ...