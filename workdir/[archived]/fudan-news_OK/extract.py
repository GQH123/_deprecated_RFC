import os
import shutil


def extract_news_json(to='news'):
    if not os.path.exists(to):
        os.makedirs(to)
    for root, dirs, files in os.walk('saves'):
        if 'news.json' in files:
            news_id = root.split('/')[-1]
            try:
                shutil.copyfile(os.path.join(root, 'news.json'), os.path.join(to, f'{news_id}.json'))
            except Exception as e:
                print(e)
                print(f'Failed to copy {news_id}')


if __name__ == '__main__':
    extract_news_json()