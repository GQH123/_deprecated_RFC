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


# manually maintained arxiv tags
# https://papers.cool/arxiv/{arxiv_tag}?show=200000
arxiv_tags = [
    'cs.AI',
    'cs.CV',
    'cs.CL',
    'cs.LG',
]


type_tag_dict = {
    'venue': venue_tags,
    'arxiv': arxiv_tags,
}


_test_fixed_cookies = {
    'client_id': "!P3n0PpTkvLxE77zUkxZw6Q==?gAWVKgAAAAAAAACMCWNsaWVudF9pZJSMGDM3MDAzLTE3MTE5NjE1NzguNjY3NDIzMpSGlC4=",
}


cookies_pool = json.load(open('cookies.json'))


class PapersCoolPaperPage(ItemType):
    _name: str = 'papers_cool_paper_page'

    _logger = None
    request_arg_group = {
        'url': ('field', 'https://papers.cool/{paper_type}/{paper_tag}?show=200000'),
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
        'lib': 'aiohttp',
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
        'nproc': 12,
        'async_sema': 24,
        'wait_timeout': 20,
        'wait_sleep': 1,
        'report_step': 10,
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


def random_choose_cookies(*args, **kwargs):
    return {'client_id': random.choice(cookies_pool)}


class PapersCoolPaperKimiSection(PapersCoolPaperPage):
    _name: str = 'papers_cool_paper_kimi_section'

    _logger = None
    request_arg_group = {
        'method': ('fixed', 'post'),
        'url': ('field', '{kimi_link}'),
        'proxies': ('fixed', default_proxy_config),
        'cookies': (random_choose_cookies,),
        # 'cookies': ('fixed', _test_fixed_cookies),  # 访问过快，请11360.14秒后重试(
        'is_leaf': ('fixed', True),
        'timeout': ('fixed', None),
    }
    
    @classmethod
    def _generate(cls, item, result):
        pass


ids = [f'{type}_{tag}' for type in type_tag_dict for tag in type_tag_dict[type]]
items_kwargs = [{'paper_type': type, 'paper_tag': tag} for type in type_tag_dict for tag in type_tag_dict[type]]
PapersCoolPaperPage._add_items(ids=ids, items_kwargs=items_kwargs, bloodline=[])
PapersCoolPaperPage.start()

# PapersCoolCookies.start(ids=range(100))