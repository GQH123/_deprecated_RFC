import time
import json
import asyncio
import random
import requests
from datetime import datetime
from fake_useragent import UserAgent

from utils import log
from config import fetch_config, web_config

ua = UserAgent()
headers = web_config.get('headers', {})
global_proxy_data = {}
# authKey = "D6FL1CJ8"
# password = "9FC1ADB88090"

request_timeout = web_config.get('request_timeout', None)


def random_chr() -> None:
    _ord = random.randint(0, 61)
    if _ord < 10:
        return chr(ord('0') + _ord)
    elif _ord < 36:
        return chr(ord('a') + _ord - 10)
    elif _ord < 62:
        return chr(ord('A') + _ord - 36)
    else:
        assert False


def random_str(n: int = 20) -> str:
    s = ''
    for i in range(n):
        s += random_chr()
    return s


def get_proxy_data():
    return global_proxy_data


async def apply_proxy():
    while not global_proxy_data:
        await asyncio.sleep(5)
    proxy_data = global_proxy_data
    ip = proxy_data['Data'][0]['IP']
    port = proxy_data['Data'][0]['port']
    # targetURL = "https://ip.cn/api/index?ip=&type=0"
    proxyAddr = f"{ip}:{port}"
    proxyUrl = "http://%(user)s:%(password)s@%(server)s" % {
        "user": authKey,
        "password": password,
        "server": proxyAddr,
    }
    proxies = {
        "http": proxyUrl,
        "https": proxyUrl,
    }
    return proxies


async def test_proxy(run_log):
    proxies = await apply_proxy()

    def test1():
        try:
            # url = 'https://www.zhihu.com/api/v4/questions/15/similar-questions?include=data[*].answer_count%2Cauthor%2Cfollower_count&limit=5'
            retry = 5
            while retry:
                retry -= 1
                try:
                    _headers = headers.copy()
                    _headers.update({'user-agent': ua.firefox})
                    r = requests.get(url, proxies=proxies, headers=_headers, timeout=request_timeout)
                    break
                except Exception as e:
                    time.sleep(5)
                    log(f'Error occurs when running test1, retrying\n[{type(e).__name__}], {e}', file=run_log, if_print=False)
            data = json.loads(r.text)
            if 'error' in data and 'need_login' in data['error'] and data['error']['need_login']:
                return False
            return True
        except Exception:
            return False

    def test2():
        try:
            # url = 'https://www.zhihu.com/api/v4/comment_v5/questions/577661110/root_comment?order_by=score&limit=20&offset='
            retry = 5
            while retry:
                retry -= 1
                try:
                    _headers = headers.copy()
                    _headers.update({'user-agent': ua.firefox})
                    r = requests.get(url, proxies=proxies, headers=_headers, timeout=request_timeout)
                    break
                except Exception as e:
                    time.sleep(5)
                    log(f'Error occurs when running test2, retrying\n[{type(e).__name__}], {e}', file=run_log, if_print=False)
            data = json.loads(r.text)
            if 'error' in data and 'need_login' in data['error'] and data['error']['need_login']:
                return False
            return True
        except Exception:
            return False

    return test1(), test2()


proxy_history_log_prefix = fetch_config.get('proxy_history_log_prefix', 'proxy_history')
proxy_run_log_prefix = fetch_config.get('proxy_run_log_prefix', 'proxy_run_log')


async def maintain_proxy(rank):
    global global_proxy_data
    proxy_history = open(f'{proxy_history_log_prefix}_{rank}.txt', 'w')
    run_log = open(f'{proxy_run_log_prefix}_{rank}.txt', 'w')
    while True:
        log('checking now', file=run_log, if_print=False)
        update_now = False

        proxy_data = global_proxy_data
        if proxy_data == {}:
            update_now = True
        else:
            if proxy_data['Code'] != 0:
                update_now = True
            else:
                deadline = datetime.strptime(proxy_data['Data'][0]['deadline'], "%Y-%m-%d %H:%M:%S").timestamp()
                # print(datetime.now().timestamp(), deadline)
                if datetime.now().timestamp() >= deadline:
                    update_now = True
        if update_now:
            while True:
                try:
                    log('update proxy data', file=run_log, if_print=False)
                    while True:
                        try:
                            r = requests.get(f'https://proxy.qg.net/allocate?Key={authKey}', timeout=request_timeout)
                            break
                        except Exception as e:
                            log(f'Error occurs when requesting proxy data, retrying\n[{type(e).__name__}], {e}', file=run_log, if_print=False)
                            time.sleep(5)
                    data = json.loads(r.text)
                    print(data, file=proxy_history, flush=True)
                    assert data['Code'] == 0, f"Proxy data error code is not 0, but {data['Code']}"
                    global_proxy_data = data
                    test_result = await test_proxy(run_log)
                    if test_result[0] and test_result[1]:
                        log('all tests passed', file=run_log, if_print=False)
                        break
                    else:
                        if not test_result[0]:
                            log('test1 fails', file=run_log, if_print=False)
                        if not test_result[1]:
                            log('test2 fails', file=run_log, if_print=False)
                        continue
                except Exception as e:
                    log(f'Error occurs when requesting proxy data, retrying\n[{type(e).__name__}], {e}', file=run_log, if_print=False)
                    time.sleep(5)
        else:
            log('no need to update proxy data', file=run_log, if_print=False)
            await asyncio.sleep(60)