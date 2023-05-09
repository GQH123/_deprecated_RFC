import inspect
import pkgutil
import functools
import importlib


def get_current_module_name(module_name):
    """ usage
        module_name = get_current_module_name(__name__)
    """
    return module_name.split('.')[-1]


def get_all_submodule_names(module_path, package_only=False):
    """ usage
        submodule_names = get_all_submodule_names(__path__)
    """
    submodule_names = []
    for module_importer, module_name, is_package in pkgutil.walk_packages(module_path):
        if is_package:
            submodule_names.append(('package', module_name))
        else:
            if package_only:
                continue
            submodule_names.append(('module', module_name))
    return submodule_names


def import_submodule(submodule, module_name):
    """ usage
        module = get_all_submodules_names(__path__)
    """
    return importlib.import_module('.'+submodule, module_name)


def parse_restriction(x, args_name, module_path):
    """ usage
        include = parse_restriction(self_kwargs['include'], 'include', __name__)
        exclude = parse_restriction(self_kwargs['exclude'], 'exclude', __name__)
    """
    match x:
        case 'all':
            x = True
        case None:
            x = []
        case x if all(isinstance(y, str) for y in x):
            x = x
        case _:
            unsupported_args_format(x, args_name, module_path)
    return x


def check_restriction(x, include, exclude):
    """ usage
        if not check_restriction(xxx_name, include, exclude):
            continue
    """
    if (include is True or x in include) and (exclude is not True and x not in exclude):
        return True
    else:
        return False


def return_decorated_func(func):
    @functools.wraps(func)
    async def inner_async(*args, **kwargs):
        return await func(*args, **kwargs)
    
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        return func(*args, **kwargs)

    if inspect.iscoroutinefunction(func):
        return inner_async
    else:
        return inner_func


def leaf(func):
    """ usage
        @leaf
        def func(**kwargs):
            ...
        leaves = get_leaves()
    """
    global leaves
    try:
        leaves
    except Exception:
        leaves = {}
    leaves[func.__name__] = func
    return return_decorated_func(func)


def get_leaves():
    """ usage
        @leaf
        def func(**kwargs):
            ...
        leaves = get_leaves()
    """
    global leaves
    _leaves = leaves
    leaves = {}
    return _leaves