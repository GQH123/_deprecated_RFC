import os
import inspect
from datetime import datetime

from RFC.utils.functional_utils import fill_format_str, check_fileIO
from RFC.utils.structural_utils import leaf, get_leaves
from RFC.utils.exception_utils import incorrect_param_type, incorrect_param_value


@leaf()
def init(_root, _subs, _types, **kwargs):
    global root, subs, types
    global log_dict
    root, subs, types = _root, _subs, _types
    root = fill_format_str(root, **kwargs)
    subs = fill_format_str(subs, **kwargs)
    log_dict = {}
    for log_type in types:
        types[log_type] = fill_format_str(types[log_type], **kwargs)
    if not os.path.exists(os.path.join(root, subs)):
        os.makedirs(os.path.join(root, subs))


@leaf(system=True)
def log(message, file, note, mode, if_print, from_module, if_flush, **kwargs):
    def _parse_fileIO(file):
        if not isinstance(file, str):
            incorrect_param_type('log.file', file, from_module, str)
        if file not in types:
            incorrect_param_value('log.file', file, from_module, types)
        if file not in log_dict:
            log_dict[file] = open(types[file], 'w')
        return log_dict[file]

    file = _parse_fileIO(file)
    current_time = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    if note:
        note = f'({note}) '
    if mode != 'info':
        from_module = ', from ' + inspect.getmodule(inspect.stack()[1][0]).__name__ if from_module is None else from_module
    else:
        from_module = ''
    mode = f'[{mode.upper()}] '
    result = current_time + note + mode + message + from_module
    print(result, file=file, flush=True)
    if if_print:
        print(result, flush=True)


leaves = get_leaves()