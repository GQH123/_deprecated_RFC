import inspect
import pkgutil
import functools
import importlib
from dataclasses import dataclass, field
from .functional_utils import load_object, log
from .exception_utils import StructureError, ParamError


full_module_list = None


def load_external_module(external_module_name, module_name):
    global full_module_list
    if full_module_list is None:
        full_module_list = load_object('../module_list.json', None)
    if full_module_list is None:
        raise ValueError(f"structural error: module_list.json not found! Please run compile.py first. From '{module_name}'.")
    if external_module_name not in full_module_list:
        raise ValueError(f"structural error: external module '{external_module_name}' not found! Please refer to module_list.json. From '{module_name}'.")
    return importlib.import_module(full_module_list[external_module_name], module_name)


def get_current_module_name(module_name):
    """ usage
        module_name = get_current_module_name(__name__)
    """
    return module_name.split('.')[-1]


def get_prev_module_name(level=2):
    try:
        return inspect.getmodule(inspect.stack()[level][0]).__name__
    except Exception:
        return '<unknown>'


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
    if not submodule.startswith('.'):
        submodule = '.' + submodule
    return importlib.import_module(submodule, module_name)


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


def check_function_params_contain_default(func):
    param_list = inspect.signature(func).parameters
    for param in param_list:
        if param_list[param].default != inspect._empty:
            return True
    return False


module_leaves_summary = {}


@dataclass
class ModuleLeaves():
    name: str = field(default='<unknown>')
    is_system: bool = field(default=False)
    has_init: bool = field(default=False)
    leaves: dict[str, tuple[callable, str]] = field(default_factory=dict)
    is_finished: bool = field(default=False)


def leaf(system=False, **kwargs):
    """ usage
        @leaf()
        def func(**kwargs):
            ...
        leaves = get_leaves()
    """
    def inner_leaf(func):
        nonlocal system
        # nonlocal freeze
        leaves_module = inspect.getmodule(inspect.stack()[1][0]).__name__
        if leaves_module not in module_leaves_summary:
            module_leaves_summary[leaves_module] = ModuleLeaves(
                name=leaves_module,
                is_system=False,
                has_init=False,
                is_finished=False,
            )
        current_module_leaves = module_leaves_summary[leaves_module]
        current_leaf = func.__name__
        func_state = 'normal'

        if current_module_leaves.is_finished:
            raise StructureError(f"node {leaves_module} is already finished.")

        if current_leaf in current_module_leaves.leaves:
            log("structural warning: leaf with the same name is already existed.", mode='warn', from_module=leaves_module)

        if current_leaf == 'init':
            current_module_leaves.has_init = True
            """
            if freeze:
                log("structural warning: initialization leaf can not be frozen.", mode='warn', from_module=leaves_module)
                freeze = False
            """
            if system:
                log("structural warning: initialization leaf can not be system leaf.", mode='warn', from_module=leaves_module)
                system = False
            func_state = 'init'

        if check_function_params_contain_default(func):
            raise StructureError(f"leaf {func.__name__}{inspect.signature(func)} contains default params from {leaves_module}")

        if system:
            current_module_leaves.is_system = True
            """
            if freeze:
                log("structural warning: system node leaf can not be frozen.", mode='warn', from_module=leaves_module)
                freeze = False
            """
            func_state = 'system'

        """
        if freeze:
            func_state = 'frozen'
        """

        current_module_leaves.leaves[current_leaf] = (func, func_state)

        return return_decorated_func(func)
    return inner_leaf


def get_leaves():
    """ usage
        @leaf()
        def func(**kwargs):
            ...
        leaves = get_leaves()
    """
    leaves_module = inspect.getmodule(inspect.stack()[1][0]).__name__
    if leaves_module not in module_leaves_summary:
        raise StructureError(f"node {leaves_module} is not existed.")
    current_module_leaves = module_leaves_summary[leaves_module]

    if not current_module_leaves.has_init:
        log(f"structural warning: node {leaves_module} has no init method.", mode='warn', from_module=leaves_module)

    if current_module_leaves.is_system:
        if current_module_leaves.has_init:
            if len(current_module_leaves.leaves) > 2:
                raise StructureError(f"multiple leaves for system node {leaves_module}.")
        else:
            if len(current_module_leaves.leaves) > 2:
                raise StructureError(f"multiple leaves for system node {leaves_module}.")

    # recover_globals()
    current_module_leaves.is_finished = True
    return current_module_leaves.leaves


def summary_leaves():
    failed_nodes = []
    for module in module_leaves_summary:
        if not module_leaves_summary[module].is_finished:
            failed_nodes.append(module)

    if failed_nodes:
        raise StructureError(f"some nodes failed to be initialized, including {failed_nodes}.")
    return module_leaves_summary


registered_globals = []


def register_global(name, default):
    registered_globals.append((name, default))
    assert name not in globals(), f"global '{name}' already defined"
    try:
        globals()[name] = default.copy()
    except Exception:
        globals()[name] = default


def recover_globals(exclude=None):
    if exclude is None:
        exclude = []
    for name, default in registered_globals:
        if name in exclude:
            continue
        try:
            globals()[name] = default.copy()
        except Exception:
            globals()[name] = default


"""
register_global('leaves_module', None)
register_global('system_node', False)
register_global('init_in_leaves', False)
register_global('leaves', {})
register_global('frozen', [])
"""