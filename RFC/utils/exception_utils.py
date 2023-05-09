import inspect


def get_prev_module_name(level=2):
    try:
        return inspect.getmodule(inspect.stack()[level][0]).__name__
    except Exception:
        return '<unknown>'


class ConditionOverflowError(Exception):
    def __init__(self, option, module_name=None):
        self.option = option
        self.module_name = module_name if module_name else get_prev_module_name()
        super(ConditionOverflowError, self).__init__(f'Conditions failed to cover option {repr(option)}. Error raised from {self.module_name}.')

    def __reduce__(self):
        return (ConditionOverflowError, (self.option, self.module_name))


class NotSupported(Exception):
    def __init__(self, param_name, unsupported_param, all_supported_params, module_name=None):
        self.param_name = param_name
        self.unsupported_param = unsupported_param
        self.all_supported_params = all_supported_params
        self.module_name = module_name if module_name else get_prev_module_name()
        super(NotSupported, self).__init__(f'Parameter {repr(self.param_name)} of choice {repr(self.unsupported_param)} is not supported, all supported ones are {repr(self.all_supported_params)}. Error raised from {self.module_name}.')

    def __reduce__(self):
        return (NotSupported, (self.param_name, self.unsupported_param, self.all_supported_params, self.module_name))


class FileNotFoundError(Exception):
    def __init__(self, path, module_name=None):
        self.path = path
        self.module_name = module_name if module_name else get_prev_module_name()
        super(FileNotFoundError, self).__init__(f'Path {repr(path)} does not exist. Error raised from {self.module_name}.')

    def __reduce__(self):
        return (FileNotFoundError, (self.path, self.module_name))


class FileFormatError(Exception):
    def __init__(self, path, format, module_name=None):
        self.path = path
        self.format = format
        self.module_name = module_name if module_name else get_prev_module_name()
        super(FileFormatError, self).__init__(f'Path {repr(path)} is not a file of format {repr(self.format)}. Error raised from {self.module_name}.')

    def __reduce__(self):
        return (FileFormatError, (self.path, self.format, self.module_name))


class ReadOnlyError(Exception):
    def __init__(self, obj, module_name=None):
        self.obj = obj
        self.module_name = module_name if module_name else get_prev_module_name()
        super(ReadOnlyError, self).__init__(f'Object {repr(obj)} is Read-Only thus cannot be modified. Error raised from {self.module_name}.')

    def __reduce__(self):
        return (ReadOnlyError, (self.obj, self.module_name))


class StructureError(Exception):
    def __init__(self, message, module_name=None):
        self.message = message
        self.module_name = module_name if module_name else get_prev_module_name()
        super(StructureError, self).__init__(f'{self.message}. Error raised from {self.module_name}.')

    def __reduce__(self):
        return (StructureError, (self.message, self.module_name))


class ParamError(Exception):
    def __init__(self, message, module_name=None):
        self.message = message
        self.module_name = module_name if module_name else get_prev_module_name()
        super(ParamError, self).__init__(f"{self.message}. Error raised from {self.module_name}.")

    def __reduce__(self):
        return (ParamError, (self.message, self.module_name))


class ParamTypeError(Exception):
    def __init__(self, param_name, param_value, expected_types, module_name=None):
        self.param_name = param_name
        self.param_value = param_value
        self.expected_types = expected_types
        self.module_name = module_name if module_name else get_prev_module_name()
        super(ParamTypeError, self).__init__(f"Incorrect type {repr(type(self.param_value))} of <{str(self.param_name)}={repr(self.param_value)}>, expected types are {repr(self.expected_types)}. Error raised from {self.module_name}.")

    def __reduce__(self):
        return (ParamTypeError, (self.param_name, self.param_value, self.expected_types, self.module_name))


class ParamValueError(Exception):
    def __init__(self, param_name, param_value, expected_values, module_name=None):
        self.param_name = param_name
        self.param_value = param_value
        self.expected_values = expected_values
        self.module_name = module_name if module_name else get_prev_module_name()
        super(ParamValueError, self).__init__(f"Incorrect value {repr(self.param_value)} of <{str(self.param_name)}={repr(self.param_value)}>, expected values are {repr(self.expected_values)}. Error raised from {self.module_name}.")

    def __reduce__(self):
        return (ParamValueError, (self.param_name, self.param_value, self.expected_values, self.module_name))


class ParamSettingError(Exception):
    def __init__(self, error_msg, module_name=None, **params):
        self.error_msg = error_msg
        self.params = params
        self.module_name = module_name if module_name else get_prev_module_name()
        _params = '<' + ', '.join([f'{k}={repr(v)}' for k, v in self.params.items()]) + '>'
        super(ParamSettingError, self).__init__(f"Incorrect params setting {_params}. {error_msg}. Error raised from {self.module_name}.")

    def __reduce__(self):
        return (ParamSettingError, (self.error_msg, self.params, self.module_name))

class SavingError(Exception):
    def __init__(self, obj, path, prefix_project_dir, mode, e, module_name=None, **params):
        self.obj = obj
        self.path = path
        self.prefix_project_dir = prefix_project_dir
        self.mode = mode
        self.e = e
        self.module_name = module_name if module_name else get_prev_module_name()
        super(SavingError, self).__init__(f"Error when saving {repr(obj)} to {repr(path)} under project dir {repr(prefix_project_dir)} with mode {repr(mode)}.[{type(e)}] {e}. Error raised from {self.module_name}.")

    def __reduce__(self):
        return (SavingError, (self.obj, self.path, self.prefix_project_dir, self.mode, self.e, self.module_name))