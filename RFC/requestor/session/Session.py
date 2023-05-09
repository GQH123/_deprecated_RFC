from typing import List
from functools import partial

from RFC.utils.exception_utils import ConditionOverflowError, ParamValueError
from RFC.itemset.RawItemset import RawItem

from .BaseSession import BaseSession
from .SessionConfig import SessionConfig



class Session(BaseSession):
    def _init_session_args(
        self,
        session_config: SessionConfig,
    ):
        if not self.use_session:
            self.session = None
        else:
            self.X = session_config.X
            self.common_args = ['...', ]
            self.session_specific_args = {
                'X': self.X,
                '...': ...,
            }
            request_args = self.arguments(include=self.common_args)
            request_args.update(self.session_specific_args)
            self.session = ....Session(
                **request_args
            )
        ...

    def _init_request_args(
        self,
        session_config: SessionConfig,
    ):
        self.request_specific_args = {
            '...': ...
        }
        ...

    def __init__(
        self,
        session_config: SessionConfig,
    ):
        super().__init__(session_config)
        ...

    def _request_args(
        self,
        method: str,
        excludes: dict[str, List[str]] = None,
        rename_maps: dict[str, dict[str, str]] = None,
        **kwargs,
    ):
        if excludes is None:
            excludes = {
                'get': ['...', ],
                'post': ['...', ],
            }
        if rename_maps is None:
            rename_maps = {
                'get': {
                    '...': ...,
                },
                'post': {
                    '...': ...,
                },
            }
        return super()._request_args(method, excludes, rename_maps, **kwargs)
        ...

    def _request(
        self,
        request_args: dict,
    ):
        if self.session:
            resp = self.session.request(
                **request_args
            )
        else:
            resp = ....request(
                **request_args
            )
        return resp
        ...

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
            return request_resp.body
        elif rtype == 'json':
            return request_resp.json
        else:
            return super()._request_resp(request_resp, rtype)
        ...

    def _retrieve_config(
        self,
        return_config: bool = False
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        ...
        if return_config:
            return SessionConfig(**my_attr)
        else:
            return my_attr