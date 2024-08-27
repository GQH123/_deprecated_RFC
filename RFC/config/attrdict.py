from collections.abc import Iterable


class AttrDict(dict):
    
    def _iterative_init_attrdict(self, obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict):
                    obj[key] = AttrDict(value)
                    # self._iterative_init_attrdict(value)  # no need to make recursion
                elif isinstance(value, Iterable) and not isinstance(value, str):
                    self._iterative_init_attrdict(value)
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                if isinstance(value, dict):
                    obj[i] = AttrDict(value)
                    # self._iterative_init_attrdict(value)  # no need to make recursion
                elif isinstance(value, Iterable) and not isinstance(value, str):
                    self._iterative_init_attrdict(value)
        else:
            raise NotImplementedError(f'unsupported iterable type {type(obj)}:\n{obj}')
                
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self._iterative_init_attrdict(self)
        self.__dict__ = self