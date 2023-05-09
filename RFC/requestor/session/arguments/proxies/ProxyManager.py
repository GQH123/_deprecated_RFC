from .BaseProxyManager import BaseProxyManager


class ProxyManager(BaseProxyManager):
    def __init__(
        self,
        name: str,
        request_address: str,
        rank: int,
        request_timeout: int,
        hist_log: str,
        run_log: str,
    ):
        super().__init__(
            name=name,
            request_address=request_address,
            rank=rank,
            request_timeout=request_timeout,
            hist_log=hist_log,
            run_log=run_log,
        )

    def _sub_check_update(
        self,
        proxy_info: dict = None,
    ):
        ...  # you need to implement this in sublcasses

    def _sub_apply(
        self,
        proxy_info: dict = None,
    ):
        ...  # you need to implement this in sublcasses