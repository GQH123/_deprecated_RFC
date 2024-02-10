import re
import json
import time
import requests

from RFC.item.item import ItemType


default_proxy_config = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
    'all': 'socks5://127.0.0.1:7890',
}


STEP_SIZE = 1000


def get_id(venue, page):
    if 'Submitted' in venue:
        venue_part = 'submitted'
    else:
        venue_part = venue.split(' ')[-1].lower()
    return venue_part + '_' + str(page)


class OpenReviewPapersMetadata(ItemType):
    _name: str = 'itemtype_openreview_papers_metadata'

    _logger = None
    request_arg_group = {
        'url': ('field', 'https://api2.openreview.net/notes?content.venue={venue}&details={details}&domain={domain}&limit={step_size}&offset={offset}'),
        'proxies': ('fixed', default_proxy_config),
    }
    item_arg_group = {
        'save_dir': ('auto', 'saves/{conf}/', 'subs/'),
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
        'json_saver': {},
        'result_saver': {},
    }
    requestor_args = {
        'nproc': 1,
        'async_sema': 24,
        'wait_timeout': 3,
        'wait_sleep': 1,
        'report_step': 10,
    }
    
    @classmethod
    def _generate(cls, item, result):
        data = result.json
        if len(data['notes']) == 0 or item.offset + STEP_SIZE >= int(data['count']):
            return
        conf = item.conf
        domain = item.domain
        venue = item.venue
        detail = item.detail
        offset = item.offset + STEP_SIZE
        page = item.page + 1
        id = get_id(venue, page)
        OpenReviewPapersMetadata._add_items(id, conf=conf, domain=domain, venue=venue, detail=detail, offset=offset, page=page, step_size=STEP_SIZE, bloodline=item.bloodline[:-1])  # no inherited bloodline for the next page of the same itemtype


conferences = {
    'iclr_2024': dict(
        venues=['ICLR 2024 oral', 'ICLR 2024 poster', 'ICLR 2024 spotlight', 'Submitted to ICLR 2024'],
        details=['replyCount,presentation'],
        domains=['ICLR.cc/2024/Conference'],
    ),
    'icml_2023': dict(
        venues=['ICML 2023 Poster', 'ICML 2023 OralPoster', 'Submitted to ICML 2023'],
        details=['replyCount,presentation'],
        domains=['ICML.cc/2023/Conference'],
    ),
}

offset = page = 0

for conf_name in conferences:
    conf = conferences[conf_name]
    for venue in conf['venues']:
        for detail in conf['details']:
            for domain in conf['domains']:
                id = get_id(venue, page)
                OpenReviewPapersMetadata._add_items(id, conf=conf_name, domain=domain, venue=venue, detail=detail, offset=offset, page=page, step_size=STEP_SIZE, bloodline=[])

OpenReviewPapersMetadata.start()