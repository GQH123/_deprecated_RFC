import inspect


def get_prev_module_name(level=2):
    try:
        return inspect.getmodule(inspect.stack()[level][0]).__name__
    except Exception:
        return '<unknown>'


class MiddleWare_JSONError(Exception):
    def __init__(self, msg, module_name=None):
        self.msg = msg
        self.module_name = module_name if module_name else get_prev_module_name()
        super(MiddleWare_JSONError, self).__init__(f'{self.msg}. Error raised from {self.module_name}.')

    def __reduce__(self):
        return (MiddleWare_JSONError, (self.msg, self.module_name))


class MiddleWare_UnknownFramework(Exception):
    def __init__(self, framework, module_name=None):
        self.framework = framework
        self.module_name = module_name if module_name else get_prev_module_name()
        super(MiddleWare_UnknownFramework, self).__init__(f'Unknown framework {self.framework}. Error raised from {self.module_name}.')

    def __reduce__(self):
        return (MiddleWare_UnknownFramework, (self.framework, self.module_name))