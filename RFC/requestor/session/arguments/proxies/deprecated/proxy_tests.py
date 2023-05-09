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




async def test_proxy(run_log):
    proxies = await apply_proxy()

    

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