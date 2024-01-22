from typing import Callable, Any, Optional, Tuple, List, Dict

FuncName = str
Func = FuncName | Callable
OptionalFunc = Optional[Func]
Args = Optional[Any | List]
# FuncArgsTuple = Tuple[Func, Args]
OptionalFuncArgsTuple = Tuple[OptionalFunc, Args]
# RobustFuncArgsTuple = Func | Tuple[Func] | FuncArgsTuple
RobustOptionalFuncArgsTuple = OptionalFunc | Tuple[OptionalFunc] | OptionalFuncArgsTuple
RecursiveDictStr2Callable = Dict[str, 'RecursiveDictStr2Callable' | Callable]

# Visit Status of ArgSetters

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

# Item Status

PENDING = 0
PROCESSING = 10
FAILED = 20
GENERATING = 30
FINISHED = 40

_itemStatusToName = {
    PENDING: "pending", 
    PROCESSING: "processing",
    FAILED: "failed",
    FINISHED: "finished",
}

_nameToItemStatus = {
    "pending": PENDING,
    "processing": PROCESSING,
    "failed": FAILED,
    "finished": FINISHED,
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