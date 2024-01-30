from typing import Callable, Any, Optional, Tuple, List, Dict, Union

FuncName = str
Func = FuncName | Callable
OptionalFunc = Optional[Func]
Args = List
OptionalFuncArgsTuple = Tuple[OptionalFunc, Args | Any]  # it seems that variable-length tuple annotation can not support forms like (A, B) / (A, B, B) / (A, B, B, B) before Python 3.11, with which we can use Tuple[OptionalFunc, Args | *tuple[Any, ...]] instead, refer to https://stackoverflow.com/questions/68346281/what-type-hint-for-heterogeneous-variable-length-tuple-in-python for more details
RobustOptionalFuncArgsTuple = OptionalFunc | Tuple[OptionalFunc] | OptionalFuncArgsTuple
RecursiveDictStr2Callable = Dict[str, Callable | 'RecursiveDictStr2Callable']
# FuncArgsTuple = Tuple[Func, Args]
# RobustFuncArgsTuple = Func | Tuple[Func] | FuncArgsTuple

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
    GENERATING: "generating",
}

_nameToItemStatus = {
    "pending": PENDING,
    "processing": PROCESSING,
    "failed": FAILED,
    "finished": FINISHED,
    "generating": GENERATING,
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


import multiprocessing as mp

# lazy init in case that pickle error occurs, https://stackoverflow.com/questions/36533134/cant-get-attribute-abc-on-module-main-from-abc-h-py
RFC_GLOBAL_MANAGER = None
RFC_GLOBAL_LOCK = None


def get_global_manager():  
    global RFC_GLOBAL_MANAGER
    global RFC_GLOBAL_LOCK
    if RFC_GLOBAL_MANAGER is None:
        RFC_GLOBAL_MANAGER = mp.Manager()
        RFC_GLOBAL_LOCK = RFC_GLOBAL_MANAGER.RLock()
    return RFC_GLOBAL_MANAGER


def get_global_lock():
    global RFC_GLOBAL_MANAGER
    global RFC_GLOBAL_LOCK
    if RFC_GLOBAL_MANAGER is None:
        RFC_GLOBAL_MANAGER = mp.Manager()
        RFC_GLOBAL_LOCK = RFC_GLOBAL_MANAGER.RLock()
    return RFC_GLOBAL_LOCK