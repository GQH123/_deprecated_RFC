import weakref

class B:
    def __init__(self, x):
        self.x = x
        
    def __repr__(self):
        return f'B({self.x})'

class A(B):
    q = []
    
    @classmethod
    def f(cls, ref):
        cls.q.remove(ref)
        
    @classmethod
    def g(cls, x):
        cls.q.append(weakref.ref(x, cls.f))

def weakref_mp():
    from multiprocessing import Manager
    manager = Manager()
    z = manager.list()
    x = B(10)
    print(x)

    A.g(x)
    print(z, A.q)
    z.append(x)
    print(z, A.q)
    x = 5
    print(z, A.q)

def weakref_sp():
    z = []
    x = B(10)
    print(x)

    A.g(x)
    print(z, A.q)
    z.append(x)
    print(z, A.q)
    x = 5
    print(z, A.q)
    

print('\nSingle Processing:')
weakref_sp()
print('\nMulti Processings:')
weakref_mp()