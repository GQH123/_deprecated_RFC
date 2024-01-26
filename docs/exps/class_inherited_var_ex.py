class Root:
    q = [1]
    inited = False
    
    def __init__(self):
        self.inited = True


class A(Root):
    q = [2]
    inited = False
    
    def __init__(self):
        if not self.inited:
            super().__init__()
            # self.q = super().q + self.q
            self.q = super(self.__class__, self).q + self.q
            self.inited = True


class B(A):
    q = [3]
    inited = False


class C(B):
    q = [4]
    inited = False
            

print(C().q)