from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import ConditionOverflowError, ParamTypeError, ParamValueError

from .ItemsetConfig import ItemsetConfig
from .Itemset import Itemset

from .RawItemsetConfig import RawItemsetConfig
from .RawItemset import RawItemset

all_supported_itemsets = ['default', 'raw']


@leaf()
def init(**kwargs):
    ...


def get_itemset_config(
    itemset_type: str,
    **kwargs,
):
    if itemset_type not in all_supported_itemsets:
        raise ParamValueError('itemset_type', itemset_type, all_supported_itemsets, __name__)
    if itemset_type == 'raw':
        return RawItemsetConfig(**kwargs)
    elif itemset_type == 'default':
        return ItemsetConfig(**kwargs)
    else:
        raise ConditionOverflowError(itemset_type, __name__)


@leaf(system=True)
def get_itemset(
    itemset_config: str | ItemsetConfig,
    **kwargs,
):
    if isinstance(itemset_config, str):
        itemset_type = itemset_config
        itemset_config = get_itemset_config(itemset_type, **kwargs)
    else:
        itemset_type = type(itemset_config).__name__
        if itemset_type == 'ItemsetConfig':
            itemset_type = 'default'
        elif itemset_type == 'RawItemsetConfig':
            itemset_type = 'raw'
        else:
            raise ParamTypeError('itemset_config', itemset_config, [ItemsetConfig, RawItemsetConfig], __name__)

    if itemset_type not in all_supported_itemsets:
        raise ParamValueError('itemset_type', itemset_type, all_supported_itemsets, __name__)
    if itemset_type == 'raw':
        return RawItemset(itemset_config)
    elif itemset_type == 'default':
        return Itemset(itemset_config)
    else:
        raise ConditionOverflowError(itemset_type, __name__)


leaves = get_leaves()