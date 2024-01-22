from RFC.core.utils.cls import RootType
from RFC.core.item.item import Item


class Requestor(RootType):
    def __init__(self):
        super().__init__()
        self._get_logger()
        
    def run(self):
        pass
    
    def _fetch_single(
        self,
        rank: int,
        item: Item,
    ):
        ...