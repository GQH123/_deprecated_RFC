class A:
    def __init__(self):
        self.f()
        ...
    def f(self):
        global x
        x.append(1)
        print(x)
  
    
from _queue import add, pop, mp


def test_1(lock, _queue):
    add(A(), lock, _queue)
    add(A(), lock, _queue)
    

def test_2(lock, _queue):
    def _init():
        add(A(), lock, _queue)
    global x
    x = []
    p1 = mp.Process(target=_init, args=())
    x.append(-1)
    p2 = mp.Process(target=_init, args=())
    p1.start()
    p2.start()
    p1.join()
    p2.join()


def test_3():
    global x
    x = []
    A().f()
    A().f()
    
    
if __name__ == '__main__':
    test_3()