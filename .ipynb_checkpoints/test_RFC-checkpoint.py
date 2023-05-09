import fire

from RFC.itemset.itemset import RawItemset

from RFC.requestor.session.RequestsSession import RequestsSession
from RFC.requestor.headers.HeadersConfig import HeadersConfig


def test_RawItemset(verbose=False):
    itemset = RawItemset(
        items=list(range(200000, 210000)),
        preprocess=None,
        url=lambda i, x: f'https://www.pixiv.net/ajax/illust/{x}',
        method='get',
    )
    if verbose:
        print(itemset)
        for item in itemset[:10]:
            print(item)
    return itemset


def test_HeadersConfig():
    return HeadersConfig()


def test_Requestor():
    ...


def test_all():
    itemset = test_RawItemset(True)
    pass


if __name__ == '__main__':
    test_all()
