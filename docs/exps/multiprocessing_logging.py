import os
import sys
import time
import logging
from functools import partial
from multiprocessing import Process, Manager
from RFC.core.utils.log import get_logger, add_handler


def worker(i, logger, lock):
    # logger.addHandler(logging.StreamHandler(sys.stdout))
    # add_handler(logging.StreamHandler(sys.stdout))
    # print(logger.handlers)
    sub_ls = manager.list([])
    for k in range(i, i+5):
        sub_ls.append(k)
    logger.warning(f'Test! {i} {sub_ls}')
    # logger.warning('Test!'*1000)
    
q = []

def worker_2(i, q):
    q.append(i)
    print(q)


if __name__ == '__main__':
    manager = Manager()
    logger = get_logger('RFC')
    # logger.addHandler(logging.FileHandler('test.log', 'w'))
    # logger.warning('Test!'*1000)
    print(logger.handlers)
    lock = manager.Lock()
    
    p = []
    for i in range(50):
        p.append(Process(target=partial(worker, logger=logger, lock=lock), args=(i,)))
        # p.append(Process(target=worker_2, args=(i,q)))
    for _p in p:
        _p.start()
    time.sleep(1)
    for i in range(50):
        p[i].join()
    print(logger.handlers)
    
    """
    with manager.Pool(10) as pool:
        pool.map(partial(worker, logger=logger, lock=lock), range(500))
    """