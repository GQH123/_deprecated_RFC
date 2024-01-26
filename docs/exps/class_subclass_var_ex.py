class A:
    x = []
    
    def __init__(self):
        super().__init__()
        print('in A')
        print(self.__class__.__name__, id(self))
        print(self.x)
        

class B(A):
    x = []
    
    def __init__(self):
        print('in B')
        print(self.__class__.__name__, id(self))
        super().__init__()
    

class C(B):
    x = []
    
    def __init__(self):
        print('in C')
        print(self.__class__.__name__, id(self))
        super(A, self).__init__()


class D(C):
    x = []
    
    def __init__(self):
        print('in D')
        print(self.__class__.__name__, id(self))
        super().__init__()


A.x.append(1)
B.x.append(2)
C()
print('-----------')
B()
print('-----------')
A()
# b = B()