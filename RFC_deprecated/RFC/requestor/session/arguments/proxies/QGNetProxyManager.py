from datetime import datetime

from .ProxyManager import ProxyManager


class QGNetProxyManager(ProxyManager):
    def __init__(
        self,
        username: str,
        password: str,
        hist_log: str,
        run_log: str,
        rank: int = -1,
        request_timeout: int = 5,
    ):
        self.authKey = username
        self.password = password
        super().__init__(
            name='QGNet',
            request_address=f'https://proxy.qg.net/allocate?Key={self.authKey}',
            rank=rank,
            request_timeout=request_timeout,
            hist_log=hist_log,
            run_log=run_log,
        )

    def _sub_check_update(
        self,
        proxy_info: dict = None,
    ):
        checked_proxy_info = self.proxy_info if proxy_info is None else proxy_info
        if checked_proxy_info is None:
            return True
        if checked_proxy_info['Code'] != 0:
            return True
        deadline = datetime.strptime(checked_proxy_info['Data'][0]['deadline'], "%Y-%m-%d %H:%M:%S").timestamp()
        if datetime.now().timestamp() >= deadline:
            return True
        return False

    def _sub_apply(
        self,
        proxy_info: dict = None,
    ):
        applied_proxy_info = self.proxy_info if proxy_info is None else proxy_info
        ip = applied_proxy_info['Data'][0]['IP']
        port = applied_proxy_info['Data'][0]['port']
        # targetURL = "https://ip.cn/api/index?ip=&type=0"
        proxyUrl = "http://%(user)s:%(password)s@%(server)s" % {
            "user": self.authKey,
            "password": self.password,
            "server": f"{ip}:{port}",
        }
        proxies = {
            "http": proxyUrl,
            "https": proxyUrl,
        }
        return proxies