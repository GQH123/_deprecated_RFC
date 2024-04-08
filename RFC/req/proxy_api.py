import os
import time
import requests
import functools
from datetime import datetime
import multiprocessing as mp

from ..utils.ds import AttrDict
from ..utils.log import get_logger
from ..utils.cls import RootType
from ..utils.defs import (
    ProxyAPI_logger_enable_file_handler,
)

logger = get_logger(__name__)
logger.info(f"importing module {__name__}")


class PoolProxyAPI(AttrDict, RootType):
    _name: str = 'proxy_api'
    
    def __init__(
        self,
        proxy_pool,
    ):
        self._get_logger_self(__name__, add_file_handler=ProxyAPI_logger_enable_file_handler, level='info')  # if loggers in multiprocessing intervening with each other, we will add special file handler for multiprocessing manually
        self.proxy_pool = proxy_pool

    def apply(
        self,
    ):
        process_name = mp.current_process().name
        assert process_name.startswith('requestor-worker-'), f'process_name {process_name} not recognized'
        process_id = int(process_name.split('-')[-1])
        assert process_id < len(self.proxy_pool), f'process_id {process_id} out of range, proxy_pool length {len(self.proxy_pool)}'
        return self.proxy_pool[process_id]


class QGNetProxyAPI(AttrDict, RootType):
    _name: str = 'proxy_api'
    
    def __init__(
        self,
        proxy_api_key: str,
        proxy_api_passwd: str,
    ):
        self._get_logger_self(__name__, add_file_handler=ProxyAPI_logger_enable_file_handler, level='info')  # if loggers in multiprocessing intervening with each other, we will add special file handler for multiprocessing manually
        proxy_api_url = f'https://share.proxy.qg.net/get?key={proxy_api_key}&distinct=true'
        self.proxy_api_info = {
            'url': proxy_api_url,
            'key': proxy_api_key,
            'passwd': proxy_api_passwd,
        }
        self._log_dir = 'saved_logs'
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir, exist_ok=True)
        self.proxy_info = None
        self.request_timeout = 1

    def _request(
        self,
    ):
        while True:
            try:
                r = requests.get(self.proxy_api_info['url'], timeout=self.request_timeout)
                new_proxy_info = r.json()
                if self._check_update(new_proxy_info):
                    raise ValueError("proxy is unavailable")
                self.proxy_info = new_proxy_info
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open('saved_logs/proxy_history.txt', 'a') as f:
                    f.write(f'[{current_time}] {new_proxy_info}\n')
                break
            except Exception as e:
                error_report = f'[{repr(type(e).__name__)}] {repr(e)}'
                self._logger.error(f"failed to request proxy info, caught error {error_report}")

    def _update(
        self,
    ):
        self._logger.info('updating proxy')
        self._request()
        self._logger.info('proxy updated successfully')

    def _sub_check_update(
        self,
        proxy_info: dict = None,
    ):
        proxy_info = proxy_info or self.proxy_info
        if proxy_info is None:
            return True
        if proxy_info['code'] != 'SUCCESS':
            return True
        deadline = datetime.strptime(proxy_info['data'][0]['deadline'], "%Y-%m-%d %H:%M:%S").timestamp()
        if datetime.now().timestamp() >= deadline:
            return True
        return False

    def _sub_apply(
        self,
        proxy_info: dict = None,
    ):
        proxy_info = proxy_info or self.proxy_info
        server = proxy_info['data'][0]['server']
        proxyUrl = "http://%(user)s:%(password)s@%(server)s" % {
            "user": self.proxy_api_info['key'],
            "password": self.proxy_api_info['passwd'],
            "server": server,
        }
        proxies = {
            "http": proxyUrl,
            "https": proxyUrl,
        }
        return proxies

    def _check_update(
        self,
        proxy_info = None,
    ):
        self._logger.info('checking if proxy need to be updated')
        return self._sub_check_update(proxy_info or self.proxy_info)

    def apply(
        self,
        proxy_info = None,
    ):
        if self._check_update():
            self._update()
        return self._sub_apply(proxy_info or self.proxy_info)


# ------------------------------------ Module Postprocess ------------------------------------ #

_nameToProxyAPI = {
    'qgnet': QGNetProxyAPI,
    'pool': PoolProxyAPI,
}

__all__ = [cls.__name__ for cls in list(_nameToProxyAPI.values())] + ['get_proxy_api']


def get_proxy_api(proxy_api_type, proxy_api_info):
    try:
        return _nameToProxyAPI[proxy_api_type](**proxy_api_info)
    except Exception as e:
        if logger is not None:
            error_report = f'[{repr(type(e).__name__)}] {repr(e)}'
            logger.error(f"failed to initialize proxy_api {repr(proxy_api_type)} with args {repr(proxy_api_info)}, caught error {error_report}")
        raise e


logger.info(f"module {__name__} imported")