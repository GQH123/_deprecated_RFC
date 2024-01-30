import os
import time
from functools import partial

from multiprocessing import Process

from lock import MANAGER, MANAGER_LOCK


class Queue:
    _queue = MANAGER.list()
    
    @classmethod
    def add(cls, x):
        with MANAGER_LOCK:
            cls._queue.append(x)
    
    @classmethod
    def get(cls):
        with MANAGER_LOCK:
            if not cls._queue:
                return None
            return cls._queue.pop()




def f(i):
    Queue.add(i)
    print(Queue._queue)
    print(Queue.get())
    
    
process = []
for i in range(64):
    process.append(Process(target=f, args=(i,)))
    process[i].start()
for i in range(64):
    process[i].join()