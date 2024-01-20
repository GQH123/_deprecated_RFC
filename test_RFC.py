import os

from RFC.core.args.arg_group import RequestArgGroup
from RFC.core.utils.log import (
    enable_explicit_format,
    set_verbosity_info,
    set_verbosity_warning,
)
from RFC.core.utils.defs import (
    allSupportedRequestLibsMapping,
    allSupportedRequestLibsNames,
)

enable_explicit_format()
set_verbosity_info()


def _test_RequestArgGroup():
    request_arg_group = RequestArgGroup(
        url=('fixed', 'https://www.renatus.com/dasd/dsa/dsd'),
    )
    print(request_arg_group)
    print(repr(request_arg_group))
    print(request_arg_group('a', 'requests'))
  
  
if __name__ == '__main__':
    _test_RequestArgGroup()
    print(allSupportedRequestLibsMapping)
    print(allSupportedRequestLibsNames)