import multiprocessing as mp


def f(i, x, lock):
    with lock:
        x.append(i)
        print(x)
    
    
def test_f(_lock):
    manager = mp.Manager()
    lock = manager.RLock()
    x = manager.list()
    p = []
    for i in range(5):
        p.append(mp.Process(target=f, args=(i, x, lock)))
        p[i].start()
    for i in range(5):
        p[i].join()
        

def test_test_f():
    manager = mp.Manager()
    lock = manager.RLock()
    p = []
    for i in range(5):
        p.append(mp.Process(target=test_f, args=(lock,)))
        p[i].start()
    for i in range(5):
        p[i].join()


test_test_f()