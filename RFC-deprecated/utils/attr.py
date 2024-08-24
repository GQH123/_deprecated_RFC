import inspect
from typing import Callable

__all__ = [
    'get_module_path',
    'get_class_name',
    'get_class_qualname',
    'get_class_fullname',
    'get_attr_qualname',
    'get_attr_fullname',
    'get_attr_shadowed_name',
    'get_func_param',
    'get_func_param_name',
]


def get_module_path(obj, is_class=False):
    """
        return the module path of an object, such as 'torch.nn.modules.linear'
    """
    return obj.__module__


def get_class_name(obj, is_class=False):
    """
        return the name of an object, such as 'Linear'
    """
    obj_class = obj.__class__ if not is_class else obj
    return obj_class.__name__


def get_class_qualname(obj, is_class=False):
    """
        return the qualified name of an object, such as 'Linear'
    """
    obj_class = obj.__class__ if not is_class else obj
    try:
        return obj_class.__qualname__
    except:
        return obj_class.__name__


def get_class_fullname(obj, is_class=False):
    """
        return the full name of an object, such as 'torch.nn.modules.linear.Linear'
    """
    obj_class = obj.__class__ if not is_class else obj
    obj_name = get_class_qualname(obj_class, True)
    obj_module = get_module_path(obj_class, True)
    if obj_module == 'builtins':
        return obj_name  # avoid outputs like 'builtins.str'
    return obj_module+'.'+obj_name


def get_attr_qualname(x, attr: str, is_class=False):
    """
        return the qualified name of an attribute of an object, such as 'Linear.weight'
    """
    assert hasattr(x, attr), f'{repr(x)} has no attribute {repr(attr)}'
    return f'{get_class_qualname(x, is_class)}.{attr}'


def get_attr_fullname(x, attr: str, is_class=False):
    """
        return the full name of an attribute of an object, such as 'torch.nn.modules.linear.Linear.weight'
    """
    assert hasattr(x, attr), f'{repr(x)} has no attribute {repr(attr)}'
    return f'{get_class_fullname(x, is_class)}.{attr}'


def get_attr_shadowed_name(obj, attr, is_class=False):
    """
        return the shadowed attribute name of an object, such as '_Linear__weight'
        note that `attr` should start with '__'
    """
    assert attr.startswith('__'), f'{repr(attr)} is not a shadowed attribute'
    obj_class = obj.__class__ if not is_class else obj
    return f'_{get_class_name(obj_class, True)}{attr}'


def get_func_param(func: Callable, repr: bool = True):
    """
        return the parameter list of a function, such as
        ```
        mappingproxy({'x': <Parameter "x">,
              'attr': <Parameter "attr: str">,
              'is_class': <Parameter "is_class=False">})
        ```
    """
    params = inspect.signature(func).parameters
    return params if not repr else dict(params)


def get_func_param_name(func: Callable):
    """
        return the parameter name list of a function, such as ['x', 'attr', 'is_class']
    """
    return list(get_func_param(func).keys())