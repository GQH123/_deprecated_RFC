import inspect
from functools import partial
from RFC.utils.structural_utils import get_current_module_name, get_all_submodule_names, import_submodule, parse_restriction, check_restriction


def setup(**kwargs):
    submodules = []
    self_kwargs = kwargs.get('kwargs', {})
    result = {}
    module_list = {}
    module_name = get_current_module_name(__name__)
    for submodule_type, submodule_name in get_all_submodule_names(__path__):
        if submodule_type == 'package':
            submodule = import_submodule(submodule_name, __name__)
            result[submodule_name], _module_list = submodule.setup(**kwargs.get(submodule_name, {}))
            module_list.update(_module_list)
        elif submodule_name == module_name:
            submodule = import_submodule(submodule_name, __name__)
            if 'init' in submodule.leaves:
                result['options'] = {'init': (str(inspect.signature(submodule.leaves['init'][0])), submodule.leaves['init'][1])}
            result['options'] = {func_name: (str(inspect.signature(func[0])), func[1]) for func_name, func in submodule.leaves.items() if func_name != 'init'}
    _result = result['options']
    del result['options']
    result['options'] = _result

    _module_name = module_name
    step = 0
    while _module_name in module_list:
        step += 1
        _module_name = f'{module_name}_{step}'
    module_list[_module_name] = __name__
    return result, module_list


def init(**kwargs):
    self_kwargs = kwargs.get('kwargs', {})
    self_params = kwargs.get('params', {})
    include = parse_restriction(self_kwargs.get('include', 'all'), 'include', __name__)
    exclude = parse_restriction(self_kwargs.get('exclude', 'none'),  'exclude', __name__)
    result = {}
    module_name = get_current_module_name(__name__)
    for submodule_type, submodule_name in get_all_submodule_names(__path__):
        if not check_restriction(submodule_name, include, exclude):
            continue
        if submodule_type == 'package':
            submodule = import_submodule(submodule_name, __name__)
            result[submodule_name] = submodule.init(**kwargs.get(submodule_name, {}))
        elif submodule_name == module_name:
            submodule = import_submodule(submodule_name, __name__)
            _result = {}
            if 'init' in submodule.leaves:
                submodule.leaves['init'][0](**self_params.get('init', {}))
            _result.update({func_name: (partial(submodule.leaves[func_name][0], **self_params.get(func_name, {})), submodule.leaves[func_name][1]) for func_name in submodule.leaves if func_name != 'init'})
            result['options'] = _result
    return result