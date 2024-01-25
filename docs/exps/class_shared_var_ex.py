class A:
    x = []
    
    def __init__(self):
        ...
        
    @classmethod
    def f(cls):
        cls.x.append(1)
        

class B(A):
    def __init__(self):
        ...
        
    @classmethod
    def f(cls):
        cls.x.append(1)


a = A()
print(a.x)
a.x.append(1)
print(a.x)
b = A()
print(a.x)
print(b.x)
c = B()
print(c.x)
B.f()
print(c.x)