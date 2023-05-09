import requests

from RFC.utils.BaseModule import BaseModule
from RFC.utils.functional_utils import log, pretty_print, retry


class BaseProxyManager(BaseModule):
    def __init__(
        self,
        name: str,
        request_address: str,
        rank: int,
        request_timeout: int,
        hist_log: str,
        run_log: str,
    ):
        self.name = name
        self.request_address = request_address
        self.rank = rank
        self.request_timeout = request_timeout
        self.hist_log = hist_log
        self.run_log = run_log
        self.proxy_info = None

    def _request(
        self,
    ):
        @retry(log_file=self.run_log, retry_times='forever', note=self.name, from_module=__name__)
        def request():
            r = requests.get(self.request_address, timeout=self.request_timeout)
            new_proxy_info = r.json()
            if not self._check_update(self, new_proxy_info, if_log=False):
                raise ValueError("Proxy is corrupted")
            # self._test(new_proxy_info)
            self.proxy_info = new_proxy_info
            log(message=pretty_print(self.proxy_info), file=self.hist_log, note=self.name)
        request()

    def _update(
        self,
    ):
        log(message='updating proxy', file=self.run_log, note=self.name)
        self._request()
        log(message='proxy updated successfully', file=self.run_log, note=self.name)

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

    def _check_update(
        self,
        proxy_info: dict = None,
        if_log: bool = True,
    ):
        if if_log:
            log(message='checking if proxy need to be updated', file=self.run_log, note=self.name)
        checked_proxy_info = self.proxy_info if proxy_info is None else proxy_info
        if checked_proxy_info is None:
            return True
        return self._sub_check_update(checked_proxy_info)

    def apply(
        self,
        proxy_info: dict = None,
    ):
        if self._check_update():
            self._update()
        applied_proxy_info = self.proxy_info if proxy_info is None else proxy_info
        return self._sub_apply(applied_proxy_info)

    def _test(
        self,
        proxy_info: dict = None,
    ):
        return True

    """ [deprecated]
    def _test(
        self,
        proxy_info: dict = None,
    ):
        tested_proxy_info = self.proxy_info if proxy_info is None else proxy_info
        test_result = self._test(new_proxy_info)
        all_result = True
        for name, result in test_result:
            if not result:
                # log(msg=f'proxy fails on test {name}', file=self.run_log, note=self.name)
                all_result = False
        if not all_result:
            raise ValueError("Proxy did not pass all tests")
    """