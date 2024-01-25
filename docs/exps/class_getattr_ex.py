from typing import Any


class A():
    def __getattr__(self, name):
        print(f"get attr {name}")
        return super().__getattr__(name)
    
    
    def __getattribute__(self, __name: str) -> Any:
        print(f"$ get attribute {__name}")
        return getattr(self, __name)
    
    def __init__(self, name):
        self.name = name
        self._x = 5
        self.__y = 7
        self.z = 9
        print("init")
        print(self.name, self._x, self.__y, self.z)
        
        
a = A('R')
print(a.z)
print(a.__dict__)