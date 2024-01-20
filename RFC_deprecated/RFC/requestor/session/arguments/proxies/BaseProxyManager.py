import time
import requests
import functools

from RFC.utils.BaseModule import BaseModule
from RFC.utils.functional_utils import log, pretty_print, update_output_channels, get_prev_module_name
from RFC.utils.exception_utils import ParamValueError


def retrying(retry_times:int|str='forever', sleep_time=1, **kwargs):  # used only in manager class
    if retry_times == 'forever':
        retry_times = -1
    elif isinstance(retry_times, int):
        if retry_times < 0:
            retry_times = -1
    else:
        raise ParamValueError('retry_times', retry_times, ['forever'], get_prev_module_name(1))

    note = kwargs.get('note', 'Retrying')
    mode = kwargs.get('mode', 'warning')
    from_module = kwargs.get('from_module', get_prev_module_name(1))
    async_framework = kwargs.get('async_framework', None)

    def returned_func(func):
        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            nonlocal retry_times
            while retry_times != 0:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    log(message=f'retrying({retry_times}), <{type(e)}> {e}', file='proxy_run_log', note=note, mode=mode, from_module=from_module)
                    retry_times = retry_times-1 if retry_times > 0 else retry_times
                    time.sleep(sleep_time)
        return wrapped_func
    return returned_func


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

        update_output_channels('proxy_run_log', open(self.run_log, 'a'))
        update_output_channels('proxy_hist_log', open(self.hist_log, 'a'))

    @retrying(retry_times='forever')
    def _request(
        self,
    ):
        r = requests.get(self.request_address, timeout=self.request_timeout)
        new_proxy_info = r.json()
        if not self._check_update(self, new_proxy_info, if_log=False):
            raise ValueError("Proxy is corrupted")
        # self._test(new_proxy_info)
        self.proxy_info = new_proxy_info
        log(message=pretty_print(self.proxy_info), file='proxy_hist_log', note=self.name)

    def _update(
        self,
    ):
        log(message='updating proxy', file='proxy_run_log', note=self.name)
        self._request()
        log(message='proxy updated successfully', file='proxy_run_log', note=self.name)

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
            log(message='checking if proxy need to be updated', file='proxy_run_log', note=self.name)
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