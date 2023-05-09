import fire

from RFC import *


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


def test_ArgumentsConfig():
    return ArgumentsConfig()


def test_Requestor():
    ...


def test_all():
    project_config = ProjectConfig(
        name='my_project_config',
        project_name='test',
    )
    itemset = test_RawItemset(True)
    pass


def test_all_configs():
    test_list = [
        'rawitemset',
        'itemset',
        'requestor',
        'session',
        'requests',
        'asks',
        'aiohttp',
        'arguments',
        'arguments-myproxy',
        'project',
    ]
    for test_config in test_list:
        print(f'===============================================\n')
        config = get_config(test_config)
        config.print()
        print(repr(config))
        print()


def test_pipeline():
    def get_itemset():
        itemset_config = get_config('rawitemset')
        print(itemset_config)
        itemset_config = itemset_config(

        )

        return RawItemset(
            items=list(range(200000, 210000)),
            preprocess=None,
            url=lambda i, x: f'https://www.pixiv.net/ajax/illust/{x}',
            method='get',
        )
    
    def get_requestor():
        requestor_config = get_config('requestor')
        return Requestor(
            session=get_session(),
            requestor_config=requestor_config,
        )

    
    itemset = get_itemset()



if __name__ == '__main__':
    # test_all_configs()
    # test_all()
    test_pipeline()
    ...