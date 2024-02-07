import multiprocessing as mp
import logging

class A:
    def __init__(self, name):
        self.logger = logging.getLogger('A')
        print(id(self.logger))
        self.logger.addHandler(logging.FileHandler(f'A_{name}.log'))
        print(self.logger.handlers)
        # self._handers = self.logger.handlers
        # this way handlers will lost in multiprocessing settings
        
        
manager = mp.Manager()
lock = manager.RLock()
_queue = manager.list()


def add(x):
    with lock:
        _queue.append(x)
        
        
def pop():
    with lock:
        return _queue.pop()
        
        
def test_1():
    add(A(1))
    add(A(2))
    A(3)
    # [<FileHandler /XXX/A_1.log (NOTSET)>]
    # [<FileHandler /XXX/A_1.log (NOTSET)>, <FileHandler /XXX/A_2.log (NOTSET)>]
    # [<FileHandler /XXX/A_1.log (NOTSET)>, <FileHandler /XXX/A_2.log (NOTSET)>, <FileHandler /XXX/A_3.log (NOTSET)>]
    
    
def test_2():
    def _init(x):
        a = A(x)
        add(a)
        print(a.logger.handlers)
    p1 = mp.Process(target=_init, args=(1,))
    p2 = mp.Process(target=_init, args=(2,))
    p3 = mp.Process(target=_init, args=(3,))
    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()
    # [<FileHandler /XXX/A_1.log (NOTSET)>]
    # [<FileHandler /XXX/A_2.log (NOTSET)>]
    # [<FileHandler /XXX/A_3.log (NOTSET)>]


test_2()

# print(id(logging.getLogger('A')))

a1 = pop()
a1.logger.info('Good!')
print(a1.logger.handlers, id(a1.logger))
a2 = pop()
a2.logger.info('Good!')
print(a2.logger.handlers, id(a2.logger))

del a1
print(a2.logger.handlers)

# a = pop()
# a.logger.info('Good!')
# print(a.logger.handlers)

# []
# []
# []