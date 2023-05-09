import importlib
from RFC.utils.structural_utils import get_current_module_name, get_all_submodule_names, import_submodule, parse_restriction, check_restriction


def setup(**kwargs):
    self_kwargs = kwargs.get('kwargs', {})
    result = {}
    module_name = get_current_module_name(__name__)
    for submodule_type, submodule_name in get_all_submodule_names(__path__):
        submodule = import_submodule(submodule_name, __name__)
        if submodule_type == 'package':
            result[submodule_name] = submodule.setup(**kwargs.get(submodule_name, {}))
        else:
            if submodule_name != module_name:
                continue
            result['options'] = list(submodule.leaves)
    _result = result['options']
    del result['options']
    result['options'] = _result
    return result


def init(**kwargs):
    global inited_module
    self_kwargs = kwargs.get('kwargs', {})
    self_params = self_kwargs.get('params', {})
    include = parse_restriction(self_kwargs.get('include', 'all'), 'include', __name__)
    exclude = parse_restriction(self_kwargs.get('exclude', None),  'exclude', __name__)
    result = {}
    inited_module = []
    for submodule_type, submodule_name in get_all_submodule_names(__path__):
        if not check_restriction(submodule_name, include, exclude):
            continue
        inited_module.append(submodule_name)
        submodule = import_submodule(submodule_name, __name__)
        if submodule_type == 'package':
            result[submodule_name] = submodule.init(**kwargs.get(submodule_name, {}))
        else:
            _result = {}
            for func_name in submodule.leaves:
                _result[func_name] = partial(submodule.leaves[func_name], **self_params.get(func_name, {}))
            result[submodule_name] = _result
    return {get_current_module_name(__name__): result}