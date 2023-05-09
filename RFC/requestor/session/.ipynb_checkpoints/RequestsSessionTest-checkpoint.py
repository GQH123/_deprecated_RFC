import fire

from RFC.itemset.RawItemset import RawItemset

from .RequestsSession import RequestsSession


def test_all():
    itemset = RawItemset(
        items=list(range(200000, 210000)),
        preprocess=None,
        url=lambda x: f'https://www.pixiv.net/ajax/illust/{x}',
        method='get',
    )
    print(itemset)
    pass


if __name__ == '__main__':
    test_all()