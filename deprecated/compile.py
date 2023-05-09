import RFC.requestor as requestor, RFC.crawler as crawler
from settings import setup_settings
from RFC.utils.functional_utils import save_object


def setup(**kwargs):
    result = {}
    result['requestor'] = requestor.setup(**kwargs.get('requestor', {}))
    result['crawler'] = requestor.setup(**kwargs.get('crawler', {}))
    save_object(result, 'references.json')


if __name__ == '__main__':
    setup(**setup_settings)