from typing import Callable, Any, Optional, Tuple, List

FuncName = str
Func = FuncName | Callable
OptionalFunc = Optional[Func]
Args = Optional[Any | List]
FuncArgsTuple = Tuple[Func, Args]
OptionalFuncArgsTuple = Tuple[OptionalFunc, Args]
RobustFuncArgsTuple = Func | Tuple[Func] | FuncArgsTuple
RobustOptionalFuncArgsTuple = OptionalFunc | Tuple[OptionalFunc] | OptionalFuncArgsTuple

UNVISITED = 0
VISITING = 1
VISITED = 2

_visitStatusToName = {
    UNVISITED: "unvisited", 
    VISITING: "visiting",
    VISITED: "visited",
}

_nameToVisitStatus = {
    "unvisited": UNVISITED,
    "visiting": VISITING,
    "visited": VISITED,
}

allSupportedRequestLibsMapping = {}

try:
    import requests
    allSupportedRequestLibsMapping['requests'] = requests
except ImportError:
    pass

try:
    import aiohttp
    allSupportedRequestLibsMapping['aiohttp'] = aiohttp
except ImportError:
    pass

"""
try:
    import urllib3
    allSupportedRequestLibsMapping['urllib3'] = urllib3
except ImportError:
    pass

try:
    import httpx
    allSupportedRequestLibsMapping['httpx'] = httpx
except ImportError:
    pass

try:
    import httpie
    allSupportedRequestLibsMapping['httpie'] = httpie
except ImportError:
    pass

try:
    import pycurl
    allSupportedRequestLibsMapping['pycurl'] = pycurl
except ImportError:
    pass
"""

allSupportedRequestLibsNames = list(allSupportedRequestLibsMapping.keys())