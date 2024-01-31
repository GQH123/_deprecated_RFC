import logging

from RFC.args.arg_group import RequestArgGroup
from RFC.utils.log import (
    enable_explicit_format,
    set_verbosity_info,
    set_verbosity_warning,
    set_verbosity_debug,
    set_formatter,
)
from RFC.utils.defs import (
    allSupportedRequestLibsMapping,
    allSupportedRequestLibsNames,
)


def _test_RequestArgGroup():
    enable_explicit_format()
    set_verbosity_info()
    request_arg_group = RequestArgGroup(
        url=('fixed', 'https://www.example.com/foo/bar/baz'),
    )
    print(request_arg_group)
    print(repr(request_arg_group))
    print(request_arg_group('a', 'requests'))
    
    
def _test_logger_formatter():
    set_formatter(logging.Formatter(
        """
        %(asctime)s
        %(created)f
        %(filename)s
        %(funcName)s
        %(levelname)s
        %(levelno)s
        %(lineno)d
        %(message)s
        %(module)s
        %(msecs)d
        %(name)s
        %(pathname)s
        %(process)d
        %(processName)s
        %(relativeCreated)d
        %(thread)d
        %(threadName)s
        """
    ))
    """
        %(asctime)s             2024-01-22 02:03:42,415
        %(created)f             1705860222.415818
        %(filename)s            arg.py
        %(funcName)s            __call__
        %(levelname)s           INFO
        %(levelno)s             20
        %(lineno)d              206
        %(message)s             'UserAgentSetter' called, result: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19577'.
        %(module)s              arg
        %(msecs)d               415
        %(name)s                RFC.utils.cls.UserAgentSetter
        %(pathname)s            /.../RFC-crawlers/RFC-dev/RFC/core/args/arg.py
        %(process)d             33191
        %(processName)s         MainProcess
        %(relativeCreated)d     457
        %(thread)d              140149682435904
        %(threadName)s          MainThread
    """
    set_verbosity_info()
    request_arg_group = RequestArgGroup(
        url=('fixed', 'https://www.example.com/foo/bar/baz'),
    )
    print(request_arg_group)
    print(repr(request_arg_group))
    print(request_arg_group('a'))
    

def _test_all_supported_request_libs():
    print(allSupportedRequestLibsMapping)
    print(allSupportedRequestLibsNames)
    
  
if __name__ == '__main__':
    # print(RequestArgGroup.__qualname__)
    # _test_RequestArgGroup()
    # _test_all_supported_request_libs()
    _test_logger_formatter()
    ...
    
    
    