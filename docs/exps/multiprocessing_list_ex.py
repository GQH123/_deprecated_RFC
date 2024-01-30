from functools import partial
from multiprocessing import Process, Manager

class AttrDict(dict):
    """
        A dict of which keys can be accessed as attributes.
        
        \# DO NOT use non-special methods of `dict` on this class, such as `update`, the attributes may not be updated correctly.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            setattr(self, key, value)
        
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        super().__setitem__(name, value)
        
    def __setitem__(self, name, value):
        self.__setattr__(name, value)
        
    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except Exception:
            return None
        
    def __getitem__(self, name):
        return self.__getattr__(name)
    
    def __getstate__(self):
        ...
    
    @staticmethod
    def f():
        print('f!')
        
    @classmethod
    def g(cls):
        print(cls)


yy = {'hh': AttrDict({'a': 1, 'b': 3})}
                      
def worker_1(i, lock):
    def kk():
        print('Rena!')
    with lock:
        # sub_ls = manager.list()
        # sub_ls.append(AttrDict(x=1, y=i, c=lock))
        # x[i] = sub_ls
        x.append(AttrDict())
        print(x, id(x), id(x[0]), flush=True)
        print(yy)

if __name__ == '__main__':
    manager = Manager()
    lock = manager.RLock()
    x = manager.list([[]]*5)
    print(x, id(x), id(x[0]), flush=True)
    p = []
    for i in range(5):
        p.append(Process(target=partial(worker_1, lock=lock), args=(i,)))
        p[i].start()
    for i in range(5):
        p[i].join()
    print('[', end='')
    print(*x, sep=', ', end='')
    print(']', id(x), id(x[0]), flush=True)
    # print(x[3])