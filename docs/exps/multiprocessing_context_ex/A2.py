x = [-1, -2]


class A:
    def __init__(self):
        # self.f()
        ...
    def f(self):
        x.append(1)
        print(x)

    
from _queue import add, pop, mp


def test_1():
    add(A())
    add(A())
    

def test_2(lock, _queue):
    global x
    p1 = mp.Process(target=add, args=(A(), lock, _queue))
    # del x
    # p2 = mp.Process(target=add, args=(A(), lock, _queue))
    p1.start()
    # p2.start()
    p1.join()
    # p2.join()