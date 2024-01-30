class A:
    x = 1
    @classmethod
    def g(cls):
        print(cls)
        print(cls.x)


class B(A):
    @classmethod
    def __init__(cls):
        print('class B inited!')
        
    def f(self):
        self.__class__.g()
    x = 2


b = B()
b.f()