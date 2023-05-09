from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import NotSupportedError, ConditionOverflowError

from .ItemsetConfig import ItemsetConfig

from .Itemset import Itemset
from .RawItemset import RawItemset


@leaf()
def init(**kwargs):
    ...


@leaf(system=True)
def get_itemset(
    itemset_type: str,
    itemset_config: ItemsetConfig,
    **kwargs,
):
    all_supported_itemsets = ['default', 'raw']

    if itemset_type not in all_supported_itemsets:
        raise NotSupportedError(itemset_type, all_supported_itemsets, __name__)
    if itemset_type == 'raw':
        return RawItemset(itemset_config, **kwargs)
    elif itemset_type == 'default':
        return Itemset(itemset_config, **kwargs)
    else:
        raise ConditionOverflowError(itemset_type, __name__)


leaves = get_leaves()