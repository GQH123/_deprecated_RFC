import os
import time
from functools import partial
from multiprocessing import Pool, Manager

x = []
print(x, os.getpid(), id(x))

def f(i, lock):
    lock.acquire(timeout=0)
    x.append(i)
    print(x, os.getpid(), id(x))
    time.sleep(1)
    try:
        lock.release()
    except:
        pass
    
manager = Manager()
lock = manager.RLock()
Pool(4).map(partial(f, lock=lock), range(10))
print(x, os.getpid(), id(x))