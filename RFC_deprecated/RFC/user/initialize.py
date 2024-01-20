import RFC.requestor as requestor
import RFC.itemset as itemset
from RFC.utils.functional_utils import update_output_channels, switch_output_channel
from RFC.settings import init_settings


def init(**kwargs):
    self_kwargs = kwargs['kwargs']
    update_output_channels({
        'initialize.log': (open(self_kwargs['log_path'], 'w'), True)
    })

    requestor.init(**kwargs.get('requestor', {}))
    itemset.init(**kwargs.get('itemset', {}))

    switch_output_channel('initialize.log', False)


if __name__ == '__main__':
    init(**init_settings)