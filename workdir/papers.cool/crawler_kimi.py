import re
import os
import json
import time
import random
import requests


from RFC.item.item import ItemType
from RFC.utils.parse import (
    get_html_soup,
    parse,
)

# default_proxy_config = {
#     'http': 'http://127.0.0.1:7890',
#     'https': 'http://127.0.0.1:7890',
#     'all': 'socks5://127.0.0.1:7890',
# }

default_proxy_config = {
    'http': 'http://10.176.52.116:7890',
    'https': 'http://10.176.52.116:7890',
    'all': 'socks5://10.176.52.116:7890',
}

# manually maintained venus tags
# https://papers.cool/venue/{venue_tag}?show=200000
venue_tags = []
venue_tags += [f'INTERSPEECH.{year}' for year in range(2004, 2023+1)]
venue_tags += [f'USENIX-Sec.{year}' for year in range(2020, 2023+1)]
venue_tags += [f'NDSS.{year}' for year in range(2021, 2024+1)]
venue_tags += [f'IWSLT.{year}' for year in range(2004, 2023+1)]
venue_tags += [f'EMNLP.{year}' for year in range(2012, 2023+1)]
venue_tags += [f'ACL.{year}' for year in range(2012, 2023+1)]
venue_tags += [f'ICCV.{year}' for year in range(2019, 2023+2, 2)]
venue_tags += [f'CVPR.{year}' for year in range(2021, 2023+1)]
venue_tags += [f'NeurIPS.{year}' for year in range(2021, 2023+1)]
venue_tags += [f'ICML.{year}' for year in range(2021, 2023+1)]
venue_tags += [f'ICLR.{year}' for year in range(2021, 2024+1)]


def get_full_date_tags(st_year=2024, st_month=1, st_day=1):
    from datetime import date, timedelta

    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    start_date = date(st_year, st_month, st_day)
    end_date = date.today() + timedelta(1)
    full_dates = []
    for single_date in daterange(start_date, end_date):
        full_dates.append(single_date.strftime("%Y-%m-%d"))
    return full_dates


arxiv_date_tags = get_full_date_tags()

# manually maintained arxiv tags
# https://papers.cool/arxiv/cs.AI?date=2024-04-02&show=200000
# https://papers.cool/arxiv/{arxiv_tag}&show=200000
arxiv_tags = []
arxiv_tags += [f'cs.{tag}?date={date_tag}' for tag in ['AI', 'CV', 'CL', 'LG'] for date_tag in arxiv_date_tags]

type_tag_dict = {
    'venue': venue_tags,
    'arxiv': arxiv_tags,
}

_test_fixed_cookies = {
    'client_id': "!P3n0PpTkvLxE77zUkxZw6Q==?gAWVKgAAAAAAAACMCWNsaWVudF9pZJSMGDM3MDAzLTE3MTE5NjE1NzguNjY3NDIzMpSGlC4=",
}


class PapersCoolPaperPage(ItemType):
    _name: str = 'papers_cool_paper_page'

    _logger = None
    request_arg_group = {
        'url': ('field', 'https://papers.cool/{paper_type}/{paper_tag}{symbol}show=200000'),  # symbol is '?' if paper_type is `venue` else '&', item id will not contain this symbol
        'proxies': ('fixed', default_proxy_config),
        # 'cookies': ('field', '{cookies}'),
        'cookies': ('fixed', _test_fixed_cookies),
        'timeout': ('fixed', None),
    }
    item_arg_group = {
        'save_dir': ('auto', 'saves', 'subs'),
    }
    session_args = {
        'no_session': False,
        'lib': 'requests',
    }
    middleware_args = {
        'status_code': {
            'expected_status_codes': [200],
        },
        'basic': {},
        'content_saver': {},
        'result_saver': {},
    }
    requestor_args = {
        'nproc': 3,
        'async_sema': 1,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 1,
    }
    
    @classmethod
    def _generate(cls, item, result):
        def parse_kimi_links(resp):
            parse_config = {
                'kimi_links': {
                    ('attr', 'a', 'class', 'title-kimi', None): {}
                },
                'pdf_links': {
                    ('attr', 'a', 'class', 'title-pdf', None): {}
                },
                'title': {
                    ('attr', 'a', 'class', 'title-link', None): {}
                }
            }
            
            # kimi-links
            kimi_link_template = f'https://papers.cool/{item.paper_type}/kimi?paper='+'{}'
            kimi_links_soup = parse(get_html_soup(resp.content), parse_config['kimi_links'])
            kimi_links_id = [soup['id'] for soup in kimi_links_soup]
            kimi_links = []
            for kimi_link_id in kimi_links_id:
                assert kimi_link_id.startswith('kimi-')
                kimi_links.append(kimi_link_template.format(kimi_link_id[len('kimi-'):]))
            
            # pdf-links
            pdf_links_soup = parse(get_html_soup(resp.content), parse_config['pdf_links'])
            raw_pdf_links = [soup['onclick'].split(', ')[1] for soup in pdf_links_soup]
            pdf_links = []
            for raw_pdf_link in raw_pdf_links:
                if raw_pdf_link.startswith('\''):
                    raw_pdf_link = raw_pdf_link[1:]
                if raw_pdf_link.endswith('\''):
                    raw_pdf_link = raw_pdf_link[:-1]
                if raw_pdf_link.startswith('/pdf?url='):
                    raw_pdf_link = raw_pdf_link[len('/pdf?url='):]
                assert raw_pdf_link.startswith('http')
                pdf_links.append(raw_pdf_link)
                
            # title
            title_soup = parse(get_html_soup(resp.content), parse_config['title'])
            titles = [soup.text for soup in title_soup]
            
            assert len(kimi_links) == len(pdf_links) == len(titles)
            return kimi_links, pdf_links, titles

        if not os.path.exists(os.path.join(item.save_dir, f'{item.id}_info.json')):
            kimi_links, pdf_links, titles = parse_kimi_links(result)
            info = list(zip(kimi_links, pdf_links, titles))
            json.dump(info, open(os.path.join(item.save_dir, f'{item.id}_info.json'), 'w'), indent=4)
        else:
            info = json.load(open(os.path.join(item.save_dir, f'{item.id}_info.json'), 'r'))
            kimi_links = [i[0] for i in info]
        
        # return  # skip the kimi section
    
        ids = [f'{item.id}_'+kimi_link.split('?paper')[-1] for kimi_link in kimi_links]
        items_kwargs = [{'kimi_link': kimi_link} for kimi_link in kimi_links]
        cls._logger.info(f'count for all item ids: {len(ids)}')
        ids_items_kwargs = [(id, item_kwargs) for id, item_kwargs in zip(ids, items_kwargs) if id not in auto_skipped_ids.get('PapersCoolPaperKimiSection', set())]
        if ids_items_kwargs:
            ids, items_kwargs = zip(*ids_items_kwargs)
        else:
            ids, items_kwargs = [], []
        cls._logger.info(f'count for added item ids: {len(ids)}')
        PapersCoolPaperKimiSection._add_items(ids=ids, items_kwargs=items_kwargs, bloodline=item.bloodline)


# class PapersCoolCookies(ItemType):
#     _name: str = 'papers_cool_cookies'

#     _logger = None
#     request_arg_group = {
#         'url': ('field', 'https://papers.cool'),
#         'proxies': ('fixed', default_proxy_config),
#         'timeout': ('fixed', 20),
#     }
#     item_arg_group = {
#         'save_dir': ('auto', 'cookies', 'subs'),
#     }
#     session_args = {
#         'no_session': True,
#         'lib': 'aiohttp',
#     }
#     middleware_args = {
#         'status_code': {
#             'expected_status_codes': [200],
#         },
#         'basic': {},
#         'content_saver': {},
#         'result_saver': {},
#     }
#     requestor_args = {
#         'nproc': 1,
#         'async_sema': 24,
#         'wait_timeout': 20,
#         'wait_sleep': 1,
#     }
    
#     @classmethod
#     def _generate(cls, item, result):
#         cookies = {'client_id': dict(result.response.cookies)['client_id'].value}
#         json.dump(cookies, open(os.path.join(item.save_dir, 'cookies.json'), 'w'), indent=4)


# cookies_pool = json.load(open('cookies.json'))
# def random_choose_cookies(*args, **kwargs):
#     return {'client_id': random.choice(cookies_pool)}


def lazy_request_cookies_online(*args, **kwargs):
    try:
        assert 'kimi_link' in kwargs, 'kimi_link not in kwargs'
        url = kwargs.pop('kimi_link')
        proxies = kwargs.pop('proxies', default_proxy_config)
        
        client_cookies = {}
        for i in range(5):
            try:
                resp = requests.request('get', 'https://papers.cool/venue/NDSS.2021', proxies=proxies)
                client_cookies = dict(resp.cookies)
                assert client_cookies, 'client cookies request error: empty cookies'
                break
            except Exception as e:
                error_report = f'cookies request error: [{type(e).__name__}] {e}'
                print(error_report, flush=True)
                time.sleep(0.5)
                continue
        if not client_cookies:
            raise ValueError('client cookies request error: all retries failed')
        
        paper_key = url.split('?paper=')[-1]
        paper_type = url.split('/kimi?paper=')[0].split('https://papers.cool/')[-1]
        paper_cookies = {}
        for i in range(5):
            try:
                resp = requests.request('post', f"https://papers.cool/{paper_type}/star?key=kimi&paper={paper_key}", cookies=client_cookies, proxies=proxies)
                paper_cookies = dict(resp.cookies)
                assert paper_cookies, 'paper cookies request error: empty cookies'
                break
            except Exception as e:
                error_report = f'paper cookies request error: [{type(e).__name__}] {e}'
                print(error_report, flush=True)
                time.sleep(0.5)
                continue
        if not paper_cookies:
            raise ValueError('paper cookies request error: all retries failed')

        return {**client_cookies, **paper_cookies}
    except Exception as e:
        error_report = f'cookies request error: [{type(e).__name__}] {e}, return empty cookies'
        print(error_report, flush=True)
        return {}


proxy_pool = (
    {
        'http': 'http://127.0.0.1:10000',
        'https': 'http://127.0.0.1:10000',
        'all': 'socks5://127.0.0.1:10000',
    },
    {
        'http': 'http://127.0.0.1:10002',
        'https': 'http://127.0.0.1:10002',
        'all': 'socks5://127.0.0.1:10002',
    },
    {
        'http': 'http://127.0.0.1:10004',
        'https': 'http://127.0.0.1:10004',
        'all': 'socks5://127.0.0.1:10004',
    },
)


class PapersCoolPaperKimiSection(PapersCoolPaperPage):
    """
        Notes:
            - `timeout` 
                - If you do not want kimi to return the response, set timeout to some value but not `None`, this will click the kimi generation buttons and make the queue blocked if too fast. The admin of papers.cool can easily detect this and restart the website.
                - Otherwise, set this to `None`, this will make your crawler to get the response and more invisible.
            - `proxies`
                - Now the admin of papers.cool has prohibited the frequent access to the website from the same IP address, so you need to use proxies to avoid being blocked.
                - QGNet API is pointless if you want to get the response. It is only useful when you just want to click the kimi generation buttons and block the queue.
                - Proxy Pool can be casually specified, as long as it is durable. Then you can use the proxy one per process and set `timeout` to `None`.
                    - The admin of papers.cool will not detect frequency access to the already generated kimi sections, but only block your frequent click to the kimi generation buttons. So it's safe to use a durable proxy.
                    - To launch multiple local proxy servers, you can refer to `./dist_clash` directory.
            - `cookies`
                - Cookies will be invalid after a while (approximately 12 hours). You can execute the `extract_cookies.py` to renew the cookies.
                    - If invalid cookies are used, the website will return html contents of `无效访问` but still with status code 200. If you see this, you need to execute `remove_subs.py` first to clear such seemingly successfully fetched items.
                    - If `extract_cookies.py` cannot get the cookies, you need to check if the cookies-extracting link (in the script) is still valid.
            - `lib`
                - It seems that the admin of papers.cool has blocked the `aiohttp` library but not `requests`. So you should use the latter. In fact async requests is pointless here after the frequency of access is prohibited.
    """
    _name: str = 'papers_cool_paper_kimi_section'

    _logger = None
    request_arg_group = {
        'method': ('fixed', 'post'),
        'url': ('field', '{kimi_link}'),
        # 'proxies': ('fixed', default_proxy_config),
        # 'proxies': ('qgnet', 'D6FL1CJ8', '9FC1ADB88090'),
        'proxies': ('pool', proxy_pool),
        # 'cookies': (random_choose_cookies,),
        'cookies': ('lazy_func', lazy_request_cookies_online),
        # 'cookies': ('fixed', _test_fixed_cookies),  # 访问过快，请11360.14秒后重试(
        'is_leaf': ('fixed', True),
        # 'timeout': ('fixed', None),
        'timeout': ('fixed', None),
        'user_agent': ('random',),
        'referer': ('host',),
    }
    
    @classmethod
    def _generate(cls, item, result):
        pass


auto_skipped_ids = {}
if os.path.exists('saved_logs/auto_skipped_ids.json'):
    auto_skipped_ids = json.load(open('saved_logs/auto_skipped_ids.json', 'r'))
if os.path.exists('saved_logs/statistics_finished_status_details.json'):
    parsed_skipped_ids = json.load(open('saved_logs/statistics_finished_status_details.json', 'r'))['__all__']
    for item_type in parsed_skipped_ids:
        auto_skipped_ids[item_type] = list(set(auto_skipped_ids.get(item_type, []) + parsed_skipped_ids[item_type]))
auto_skipped_ids_count = {item_type: len(auto_skipped_ids[item_type]) for item_type in auto_skipped_ids}
print(f'count for auto_skipped_ids:\n{json.dumps(auto_skipped_ids_count, indent=4, ensure_ascii=False)}\n')
json.dump(auto_skipped_ids, open('saved_logs/auto_skipped_ids.json', 'w'), indent=4, ensure_ascii=False)
auto_skipped_ids = {item_type: set(auto_skipped_ids[item_type]) for item_type in auto_skipped_ids}

ids = [f'{type}_{tag}' for type in type_tag_dict for tag in type_tag_dict[type]]
items_kwargs = [{'paper_type': type, 'paper_tag': tag, 'symbol': '?' if type == 'venue' else '&'} for type in type_tag_dict for tag in type_tag_dict[type]]
print(f'count for all ids: {len(ids)}\n')
# ids_items_kwargs = [(id, item_kwargs) for id, item_kwargs in zip(ids, items_kwargs) if id not in auto_skipped_ids.get('PapersCoolPaperPage', set())]
# if ids_items_kwargs:
#     ids, items_kwargs = zip(*ids_items_kwargs)
# else:
#     ids, items_kwargs = [], []
print(f'count for added ids: {len(ids)}\n')

if __name__ == '__main__':
    PapersCoolPaperPage._add_items(ids=ids, items_kwargs=items_kwargs, bloodline=[])
    PapersCoolPaperPage.start()
    # PapersCoolCookies.start(ids=range(100))  
    pass