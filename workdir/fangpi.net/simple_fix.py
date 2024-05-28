import os
import re
import json
from tqdm import tqdm
import multiprocessing as mp

from RFC.utils.parse import (
    get_html_soup,
    parse,
)


savepath = 'saves/'


def parse_music_page_re_single_process(item):
    if not os.path.exists(os.path.join(savepath, item, f'{item}.html')):
        return
    text = open(os.path.join(savepath, item, f'{item}.html'), 'r').read()
    def _parse_music_page_re(text):
        info = {k: v for k, v in re.findall('window.([0-9a-z_]*) = (.*);', text)}
        info['mp3_lrc'] = [part for part in '\n'.join(re.findall('window.mp3_lrc = `((?:.*)(?:\n.*)*)`;', text, re.MULTILINE)).split('\n') if part]
        if len(info) == 1 and not info['mp3_lrc']:
            info = {}
        return info
    try:
        info = _parse_music_page_re(text)
        if info:
            json.dump(info, open(os.path.join(savepath, str(item), f'{item}_info.json'), 'w'), indent=4, ensure_ascii=False)
    except Exception as e:
        error_report = f'[{type(e).__name__}] {str(e)}'
        print(f'Error when parsing music page {item}: {error_report}')
        pass


def fix_lyrics_parse(n_workers=64):
    items = os.listdir(savepath)
    # items = ['875147', '13510000']
    with mp.Pool(n_workers) as pool:
        for _ in tqdm(pool.imap_unordered(parse_music_page_re_single_process, items), total=len(items)):
            pass
    # for item in tqdm(items):
    #     if os.path.exists(os.path.join(savepath, item, f'{item}.html')):
    #         parse_music_page_re(open(os.path.join(savepath, item, f'{item}.html'), 'r').read(), item)


if __name__ == '__main__':
    # fix_lyrics_parse()
    pass