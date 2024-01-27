class A:
    x = 1
    @classmethod
    def f(cls):
        print(cls)
        print(cls.x)


class B(A):
    x = 2


b = B()
b.f()