import os
import json
import time
import random
import requests
import functools
from datetime import datetime
import multiprocessing as mp

from ..utils.ds import AttrDict
from ..utils.log import get_logger
from ..utils.cls import RootType
from ..utils.defs import (
    ProxyAPI_logger_enable_file_handler,
    TIMEZONE_OFFSET,
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
    

class BaseProxyAPI(AttrDict, RootType):
    _name: str = 'base_proxy_api'
    
    def __init__(
        self,
        proxy_api_info: dict,
    ):
        super().__init__()
        self._get_logger_self(__name__, add_file_handler=ProxyAPI_logger_enable_file_handler, level='info')  # if loggers in multiprocessing intervening with each other, we will add special file handler for multiprocessing manually
        self.proxy_api_info = proxy_api_info
        self._log_dir = 'saved_logs'
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir, exist_ok=True)
        self.proxy_info = None
        self.request_timeout = 20
        self.tag = self._name.split('_')[0]

    def _request(
        self,
    ):
        while True:
            try:
                r = requests.get(self.proxy_api_info['url'], timeout=self.request_timeout)
                new_proxy_info = r.json()
                if self._check_update(new_proxy_info):
                    raise ValueError(f"proxy is unavailable, {new_proxy_info}")
                self.proxy_info = new_proxy_info
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(f'saved_logs/proxy_history_{self.tag}.txt', 'a') as f:
                    f.write(f'[{current_time}] {new_proxy_info}\n')
                json.dump(new_proxy_info, open(f'saved_logs/proxy_{self.tag}.json', 'w'), indent=4, ensure_ascii=False)
                break
            except Exception as e:
                error_report = f'[{repr(type(e).__name__)}] {repr(e)}'
                self._logger.error(f"failed to request proxy info, caught error {error_report}")
                time.sleep(2)

    # def update(
    #     self,
    # ):
    #     self._logger.info('updating proxy')
    #     if self._check_request():
    #         self._request()
    #     self._logger.info('proxy updated successfully')
        
    # def _sub_check_request(
    #     self,
    # ):
    #     return True  # it is True by default, however, if you want to restrict the request to some specific process, you can override this method

    def _sub_check_update(
        self,
        proxy_info: dict = None,
        ignore_deadline = False,
    ):
        raise NotImplementedError

    def _sub_apply(
        self,
        proxy_info: dict = None,
    ):
        raise NotImplementedError
    
    # def _check_request(
    #     self,
    # ):
    #     self._logger.info('checking if proxy need to be requested')
    #     return self._sub_check_request()

    def _check_update(
        self,
        proxy_info = None,
        ignore_deadline = False,
    ):
        self._logger.info('checking if proxy need to be updated')
        return self._sub_check_update(proxy_info or self.proxy_info, ignore_deadline)

    def apply(
        self,
        proxy_info = None,
        ignore_deadline = False,
    ):
        if self._check_update(ignore_deadline=ignore_deadline):
            self._logger.info('updating proxy')
            self._request()
            self._logger.info('proxy updated successfully')
        return self._sub_apply(proxy_info or self.proxy_info)


class QGNetProxyAPI(BaseProxyAPI):
    _name: str = 'qgnet_proxy_api'
    
    def __init__(
        self,
        proxy_api_key: str,
        proxy_api_passwd: str,
    ):
        super().__init__({
            'url': f'https://share.proxy.qg.net/get?key={proxy_api_key}&distinct=true',
            'key': proxy_api_key,
            'passwd': proxy_api_passwd,
        })

    def _sub_check_update(
        self,
        proxy_info: dict = None,
        ignore_deadline = False,
    ):
        proxy_info = proxy_info or self.proxy_info
        if proxy_info is None:
            return True
        if proxy_info['code'] != 'SUCCESS':
            return True
        deadline = datetime.strptime(proxy_info['data'][0]['deadline'], "%Y-%m-%d %H:%M:%S").timestamp()
        if datetime.now().timestamp() + TIMEZONE_OFFSET * 3600 >= deadline:
            return True
        if ignore_deadline:
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
    
    
class QGNetProxyBatchAPI(BaseProxyAPI):
    _name: str = 'qgnet_proxy_batch_api'
    
    def __init__(
        self,
        proxy_api_key: str,
        proxy_api_passwd: str,
        proxy_batch_size: int,
    ):
        super().__init__({
            'url': f'https://share.proxy.qg.net/get?key={proxy_api_key}&distinct=true&num={proxy_batch_size}',
            'key': proxy_api_key,
            'passwd': proxy_api_passwd,
        })
        
    def _read_proxy_info(
        self,
    ):
        try:
            if not os.path.exists(f'saved_logs/proxy_{self.tag}.json'):
                return None
            return json.load(open(f'saved_logs/proxy_{self.tag}.json'))
        except Exception as e:  # there may be some exceptions when reading the file because of the lack of locks
            return None
        
    # def _sub_check_request(
    #     self,
    # ):
    #     return mp.current_process().name == 'requestor-worker-0'

    def _sub_check_update(
        self,
        proxy_info: dict = None,
        ignore_deadline = False,
    ):
        _process_name = mp.current_process().name
        if _process_name != 'requestor-worker-0':
            # check only on the first process
            return False
        proxy_info = proxy_info or self._read_proxy_info()
        if proxy_info is None:
            return True
        if proxy_info['code'] != 'SUCCESS':
            return True
        deadline = datetime.strptime(proxy_info['data'][0]['deadline'], "%Y-%m-%d %H:%M:%S").timestamp()
        # self._logger.info(f'{datetime.now().timestamp()}, {deadline}')
        if datetime.now().timestamp() + TIMEZONE_OFFSET * 3600 >= deadline:
            return True
        # ignore_deadline is not supported in batch proxy API, we should not refresh the entire proxy_info because of the few errors
        # if ignore_deadline:
        #     return True
        return False

    def _sub_apply(
        self,
        proxy_info: dict = None,
    ):
        # _process_name = mp.current_process().name
        # _process_id = int(_process_name.split('-')[-1])
        while True:
            proxy_info = proxy_info or self._read_proxy_info()
            if proxy_info is None:
                time.sleep(1)
            else:
                break
        # proxy_num = len(proxy_info['data'])
        # server = proxy_info['data'][_process_id % proxy_num]['server']
        server = random.choice(proxy_info['data'])['server']  # better in practice
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


class ZMHTTPProxyAPI(BaseProxyAPI):
    _name: str = 'zmhttp_proxy_api'
    
    def __init__(
        self,
        proxy_api_url: str
    ):
        super().__init__({
            'url': proxy_api_url,
        })

    def _sub_check_update(
        self,
        proxy_info: dict = None,
        ignore_deadline = False,
    ):
        proxy_info = proxy_info or self.proxy_info
        if proxy_info is None:
            return True
        if not proxy_info['success']:
            return True
        deadline = datetime.strptime(proxy_info['data'][0]['expire_time'], "%Y-%m-%d %H:%M:%S").timestamp()
        if datetime.now().timestamp() + TIMEZONE_OFFSET * 3600 >= deadline:
            return True
        return False

    def _sub_apply(
        self,
        proxy_info: dict = None,
    ):
        proxy_info = proxy_info or self.proxy_info
        proxyUrl = "http://%(ip)s:%(port)s" % {
            "ip": proxy_info['data'][0]['ip'],
            "port": proxy_info['data'][0]['port'],
        }
        proxies = {
            "http": proxyUrl,
            "https": proxyUrl,
        }
        self._logger.info(str(proxies))
        return proxies


# ------------------------------------ Module Postprocess ------------------------------------ #

_nameToProxyAPI = {
    'qgnet': QGNetProxyAPI,
    'qgnet_batch': QGNetProxyBatchAPI,
    'zmhttp': ZMHTTPProxyAPI,
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