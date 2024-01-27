import os
from typing import Any, Dict

from ..utils.cls import RootType
from ..utils.ds import AttrDict
from ..utils.func import save_object
from ..utils.log import get_logger
from ..item.item import Item

from .middleware_func import (
    get_status_code,
    get_filename,
    get_fileext,
    get_json_sync,
    get_json_async,
    get_content_sync,
    get_content_async,
    get_stream_sync,
)

logger = get_logger(__name__)


class MiddlewareMeta(type):
    keyword = ['_defined_args']

    def __new__(cls, clsname, bases, attrs):
        for name, val in attrs.items():
            if not isinstance(val, dict) or name not in cls.keyword:
                continue
            inherited_dict = {}
            for base in bases:
                if hasattr(base, name):
                    inherited_dict.update(getattr(base, name))
            inherited_dict.update(val)
            attrs[name] = inherited_dict
        return super().__new__(cls, clsname, bases, attrs)


class Middleware(AttrDict, RootType, metaclass=MiddlewareMeta):
    _defined_args = {
    }  # SUBCLASS, expected init args with default value for this middleware

    def __init__(
        self,
        middleware_args: AttrDict
    ):
        _args = AttrDict()
        for arg in middleware_args:
            if arg not in self._defined_args:
                self._logger.warning(f"arg {repr(arg)} not defined in {repr(self)}")
                continue
            _args[arg] = middleware_args[arg]
        for defined_arg in self._defined_args:
            if defined_arg not in _args:
                _args[defined_arg] = self._defined_args[defined_arg]
                self._logger.info(f"arg {repr(defined_arg)} not set, using default {repr(self._defined_args[defined_arg])}")
        super().__init__(_args)
        self._get_logger()
        self._logger.info("initialized")


    def _apply_sync(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
    ):
        return result
    # SUBCLASS

    async def _apply_async(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        return result
    # SUBCLASS
    
    def _handle_error(
        self,
        error: Exception,
        item: Item,
        result: AttrDict,
    ):
        raise error
    # OPTIONAL[SUBCLASS]
        
    def apply_sync(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
    ):
        try:
            _result = self._apply_sync(item, result, request_lib)
            self._logger.info(f"applied on {repr(item)}")
            return _result
        except Exception as e:
            self._logger.info(f"failed on {repr(item)}, caught error {repr(e)}")
            self._handle_error(e, item, result)

    async def apply_async(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        try:
            _result = await self._apply_async(item, result, request_lib, async_lib)
            self._logger.info(f"applied on {repr(item)}")
            return _result
        except Exception as e:
            self._logger.info(f"failed on {repr(item)}, caught error {repr(e)}")
            self._handle_error(e, item, result)


class _Middleware(Middleware):
    _defined_args = {
    }

    def _apply_sync(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
    ):
        ...

    async def _apply_async(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        ...


class StatusCodeMiddleware(Middleware):
    _defined_args = {
        'expected_status_codes': [200],
    }

    def _apply_sync(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
    ):
        status_code = get_status_code(result.response, request_lib)     # type: ignore
        if status_code not in self.expected_status_codes:               # type: ignore
            raise ValueError(f"unexpected status code {repr(status_code)} in response of {repr(item)}")
        result.status_code = status_code
        return result

    async def _apply_async(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        return self._apply_sync(item, result, request_lib)


class BasicMiddleware(Middleware):
    _defined_args = {
    }
    
    def _apply_sync(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
    ):
        result.filename = get_filename(result.response, request_lib, repr(item.id))         # type: ignore
        result.fileext = get_fileext(result.response, request_lib)                          # type: ignore
        result.save_path = os.path.join(item.save_path, result.filename + result.fileext)   # type: ignore
        return result

    async def _apply_async(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        return self._apply_sync(item, result, request_lib)


class JSONMiddleware(Middleware):
    _defined_args = {
    }

    def _apply_sync(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
    ):
        result.json = get_json_sync(result.response, request_lib)     # type: ignore
        return result

    async def _apply_async(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        result.json = await get_json_async(result.response, request_lib)     # type: ignore
        return result


class SaverMiddleware(Middleware):
    _defined_args = {
    }
    
    def _save(self, result, content):
        if 'save_path' not in result:
            self._logger.warning(f"no save_path in {repr(result)}, skipped save, use BasicMiddleware before saving")
            return
        save_object(content, result.save_path, 'auto', self._logger)
    
    def _apply_sync(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
    ):
        content = result.json if 'json' in result else get_content_sync(result.response, request_lib)  # type: ignore
        self._save(result, content)

    async def _apply_async(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        content = result.json if 'json' in result else await get_content_async(result.response, request_lib)  # type: ignore
        self._save(result, content)


class StreamDownloaderMiddleware(Middleware):
    _defined_args = {
        'chunk_size': 1024,
    }

    def _apply_sync(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
    ):
        if 'save_path' not in result:
            raise ValueError(f"no save_path in {repr(result)}, use BasicMiddleware before downloading stream")
        return get_stream_sync(result.response, request_lib, result.save_path, self.chunk_size)  # type: ignore

    async def _apply_async(
        self,
        item: Item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        raise NotImplementedError


# ------------------------------------ Module Postprocess ------------------------------------ #

_nameToMiddleware = {
    'status_code': StatusCodeMiddleware,
    'basic': BasicMiddleware,
    'json': JSONMiddleware,
    'saver': SaverMiddleware,
    'stream_downloader': StreamDownloaderMiddleware,
}

__all__ = [cls.__name__ for cls in list(_nameToMiddleware.keys())] + ['get_middleware']


def get_middleware(middleware_args: AttrDict, logger=None):
    middleware_list = []
    for middleware_name in middleware_args:
        if middleware_name not in _nameToMiddleware:
            if logger is not None:
                logger.warning(f"middleware {repr(middleware_name)} not defined, all middleware defined are {repr(list(_nameToMiddleware.keys()))}")
        try:
            middleware_list.append(_nameToMiddleware[middleware_name](middleware_args[middleware_name]))
        except Exception as e:
            if logger is not None:
                error_report = f'[{repr(e).__name__}] {repr(e)}'
                logger.warning(f"failed to initialize middleware {repr(middleware_name)} with args {repr(middleware_args[middleware_name])}, caught error {error_report}")
    return middleware_list


def _module_postprocess():
    module_report = {}
    for var_name, var_value in globals().items():
        if var_name in __all__ and isinstance(var_value, type):
            module_report[repr(var_value.__qualname__)] = {name: repr(setter) for name, setter in var_value._defined_args.items()}
    import json
    logger.debug(f"module {__name__} loaded:\n{json.dumps(module_report, indent=4, ensure_ascii=False)}\n")
    with open(f'docs/refs/{__name__}.json', 'w') as f:
        json.dump(module_report, f, indent=4, ensure_ascii=False)


_module_postprocess()