from enum import Enum, auto


# here we will define some primitives for special operations in config, which are in fact named tuples and for type checking


class Primitive:
    def __init__(self,):
        pass


class FuncCall(Primitive):
    def __init__(self, func, args):
        super().__init__()
        self.func = func
        self.args = args
        
        
class Type(Primitive):
    def __init__(self, type, help=None):
        super().__init__()
        self.type = type
        self.help = help
        
        
class Value(Primitive):
    def __init__(self, value):
        super().__init__()
        self.value = value