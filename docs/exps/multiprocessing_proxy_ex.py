from functools import partial
from multiprocessing import Process, Manager

def worker_1(i, lock):
    with lock:
        x[i].append(i)
        print(x, id(x), id(x[0]), flush=True)

def worker_2(i, lock):
    with lock:
        sub_ls = manager.list([])
        sub_ls.append(i)
        x[i] = sub_ls
        print('[', end='')
        print(*x, sep=', ', end='')
        print(']', id(x), id(x[0]), flush=True)

if __name__ == '__main__':
    manager = Manager()
    lock = manager.Lock()
    x = manager.list([[]]*5)
    print(x, id(x), id(x[0]), flush=True)
    p = []
    for i in range(5):
        p.append(Process(target=partial(worker_2, lock=lock), args=(i,)))
        p[i].start()
    for i in range(5):
        p[i].join()
    print('[', end='')
    print(*x, sep=', ', end='')
    print(']', id(x), id(x[0]), flush=True)
    # print(x[3])