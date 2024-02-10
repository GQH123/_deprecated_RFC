import os
import json
from typing import Any, Dict

from ..utils.cls import RootType
from ..utils.ds import AttrDict
from ..utils.func import save_object
from ..utils.log import get_logger
# from ..item.item import Item  # for circular import issue we cannot import `Item` for typing
from ..args.arg_group import *
from .middleware_func import *

logger = get_logger(__name__)
logger.info(f"importing module {__name__}")


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
    _name: str = 'middleware'  # SUBCLASS
    
    _defined_args = {
    }  # SUBCLASS, expected init args with default value for this middleware

    def __init__(
        self,
        middleware_args: AttrDict
    ):
        self._get_logger_self(__name__, level='info')
        _args = AttrDict()
        for arg in middleware_args:
            if arg not in self._defined_args:
                self._logger.warning(f"arg {repr(arg)} not defined")
                continue
            _args[arg] = middleware_args[arg]
        for defined_arg in self._defined_args:
            if defined_arg not in _args:
                _args[defined_arg] = self._defined_args[defined_arg]
                self._logger.warning(f"arg {repr(defined_arg)} not set, using default {repr(self._defined_args[defined_arg])}")
        super().__init__(_args)
        self._logger.info("initialized")


    def _apply_sync(
        self,
        item,
        result: AttrDict,
        request_lib: str,
    ):
        return result
    # SUBCLASS

    async def _apply_async(
        self,
        item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        return result
    # SUBCLASS
    
    def _handle_error(
        self,
        error: Exception,
        item,
        result: AttrDict,
    ):
        raise error
    # OPTIONAL[SUBCLASS]
        
    def apply_sync(
        self,
        item,
        result: AttrDict,
        request_lib: str,
    ):
        try:
            self._logger.info(f"applying on {repr(item)}, received")
            # item._wrapped_logger.info(f"applying middleware {repr(self)} on {repr(item)}, input")
            _result = self._apply_sync(item, result, request_lib)
            self._logger.info(f"applied on {repr(item)}, sent")
            # item._wrapped_logger.info(f"applied middleware {repr(self)} on {repr(item)}, output")
            return _result
        except Exception as e:
            self._logger.error(f"failed on {repr(item)}, caught error {repr(e)}")
            # item._wrapped_logger.info(f"failed middleware {repr(self)} on {repr(item)}, caught error {repr(e)}")
            self._handle_error(e, item, result)

    async def apply_async(
        self,
        item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        try:
            self._logger.info(f"applying on {repr(item)}, received")
            # item._wrapped_logger.info(f"applying middleware {repr(self)} on {repr(item)}, input")
            _result = await self._apply_async(item, result, request_lib, async_lib)
            self._logger.info(f"applied on {repr(item)}, sent")
            # item._wrapped_logger.info(f"applied middleware {repr(self)} on {repr(item)}, output")
            return _result
        except Exception as e:
            self._logger.error(f"failed on {repr(item)}, caught error {repr(e)}")
            # item._wrapped_logger.info(f"failed middleware {repr(self)} on {repr(item)}, caught error {repr(e)}")
            self._handle_error(e, item, result)
    
    def __repr__(self):
        cls_repr = f'{repr(self.__class__.__qualname__)}'
        args_repr = repr({args: self[args] for args in self._defined_args})
        return f'{cls_repr}({args_repr})'


class _Middleware(Middleware):
    _name: str = ...

    _defined_args = {
    }

    def _apply_sync(
        self,
        item,
        result: AttrDict,
        request_lib: str,
    ):
        ...

    async def _apply_async(
        self,
        item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        ...


class StatusCodeMiddleware(Middleware):
    _name: str = 'middleware_status_code'

    _defined_args = {
        'expected_status_codes': [200],
    }

    def _apply_sync(
        self,
        item,
        result: AttrDict,
        request_lib: str,
    ):
        status_code = get_status_code(result.response, request_lib)     # type: ignore
        if status_code not in self.expected_status_codes:               # type: ignore
            raise ValueError(f"unexpected status code {repr(status_code)} in response of {repr(item)}")
        self._logger.info(f"status code {repr(status_code)} in response of {repr(item)}")
        result.status_code = status_code
        return result

    async def _apply_async(
        self,
        item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        return self._apply_sync(item, result, request_lib)


class BasicMiddleware(Middleware):
    _name: str = 'middleware_basic'
    
    _defined_args = {
        'reject_types': [],
    }
    
    def _apply_sync(
        self,
        item,
        result: AttrDict,
        request_lib: str,
    ):
        result.filename = get_filename(result.response, request_lib, str(item.id))         # type: ignore
        result.fileext = get_fileext(result.response, request_lib)                         # type: ignore
        if result.fileext and result.filename.endswith(result.fileext):
            result.filename = result.filename[:-len(result.fileext)]
        result.save_path = os.path.join(item.save_dir, result.filename + result.fileext)   # type: ignore
        # file_type = result.
        if result.fileext in self.reject_types:               # type: ignore
            raise ValueError(f"rejected type {repr(result.fileext)} in response of {repr(item)}")
        return result

    async def _apply_async(
        self,
        item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        return self._apply_sync(item, result, request_lib)


class TextSaverMiddleware(Middleware):
    _name: str = 'middleware_text_saver'
    
    _defined_args = {
    }
    
    def _save(self, item, result):
        if 'save_path' not in result:
            self._logger.warning(f"no save_path found, skipped save, use BasicMiddleware before saving")
            # item._wrapped_logger.warning(f"no save_path found, skipped save in {repr(self)}, use BasicMiddleware before saving")
            return
        save_object(result.text, result.save_path, 'text', self._logger)

    def _apply_sync(
        self,
        item,
        result: AttrDict,
        request_lib: str,
    ):
        result.text = get_text_sync(result.response, request_lib)     # type: ignore
        self._save(item, result)
        return result

    async def _apply_async(
        self,
        item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        result.text = await get_text_async(result.response, request_lib)     # type: ignore
        self._save(item, result)
        return result


class JSONSaverMiddleware(Middleware):
    _name: str = 'middleware_json_saver'
    
    _defined_args = {
    }
    
    def _save(self, item, result):
        if 'save_path' not in result:
            self._logger.warning(f"no save_path found, skipped save, use BasicMiddleware before saving")
            # item._wrapped_logger.warning(f"no save_path found, skipped save in {repr(self)}, use BasicMiddleware before saving")
            return
        save_object(result.json, result.save_path, 'json', self._logger)

    def _apply_sync(
        self,
        item,
        result: AttrDict,
        request_lib: str,
    ):
        result.json = get_json_sync(result.response, request_lib)     # type: ignore
        self._save(item, result)
        return result

    async def _apply_async(
        self,
        item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        result.json = await get_json_async(result.response, request_lib)     # type: ignore
        self._save(item, result)
        return result


class ContentSaverMiddleware(Middleware):
    _name: str = 'middleware_content_saver'
    
    _defined_args = {
    }
    
    def _save(self, item, result):
        if 'save_path' not in result:
            self._logger.warning(f"no save_path found, skipped save, use BasicMiddleware before saving")
            # item._wrapped_logger.warning(f"no save_path found, skipped save in {repr(self)}, use BasicMiddleware before saving")
            return
        save_object(result.content, result.save_path, 'auto', self._logger)
    
    def _apply_sync(
        self,
        item,
        result: AttrDict,
        request_lib: str,
    ):
        result.content = result.json if 'json' in result else get_content_sync(result.response, request_lib)  # type: ignore
        self._save(item, result)
        return result

    async def _apply_async(
        self,
        item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        result.content = result.json if 'json' in result else await get_content_async(result.response, request_lib)  # type: ignore
        self._save(item, result)
        return result


class StreamDownloaderMiddleware(Middleware):
    _name: str = 'middleware_stream_downloader'
    
    _defined_args = {
        'chunk_size': 1024,
    }

    def _apply_sync(
        self,
        item,
        result: AttrDict,
        request_lib: str,
    ):
        if 'save_path' not in result:
            raise ValueError(f"no save_path found, use BasicMiddleware before downloading stream")
        return get_stream_sync(result.response, request_lib, result.save_path, self.chunk_size)  # type: ignore

    async def _apply_async(
        self,
        item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        raise NotImplementedError


class ResultSaverMiddleware(Middleware):
    _name: str = 'middleware_result_saver'
    
    _defined_args = {
    }

    def _apply_sync(
        self,
        item,
        result: AttrDict,
        request_lib: str,
    ):
        _result = AttrDict()
        exclude = ['response', 'content'] if item.is_leaf else ['response']
        for key in result:
            if key not in exclude:
                _result[key] = result[key]
        save_object(_result, os.path.join(item.save_dir, '_result.pkl'), 'pkl', self._logger)
        return result

    async def _apply_async(
        self,
        item,
        result: AttrDict,
        request_lib: str,
        async_lib: str,
    ):
        return self._apply_sync(item, result, request_lib)


# ------------------------------------ Module Postprocess ------------------------------------ #

_nameToMiddleware = {
    'status_code': (StatusCodeMiddleware, StatusCodeMiddlewareArgs),
    'basic': (BasicMiddleware, BasicMiddlewareArgs),
    'json_saver': (JSONSaverMiddleware, JSONSaverMiddlewareArgs),
    'text_saver': (TextSaverMiddleware, TextSaverMiddlewareArgs),
    'result_saver': (ResultSaverMiddleware, ResultSaverMiddlewareArgs),
    'content_saver': (ContentSaverMiddleware, ContentSaverMiddlewareArgs),
    'stream_downloader': (StreamDownloaderMiddleware, StreamDownloaderMiddlewareArgs),
}

__all__ = [cls[0].__name__ for cls in list(_nameToMiddleware.values())] + ['get_middleware']


def get_middleware(middleware_args: AttrDict, logger=None):
    middleware_list = []
    for middleware_name in middleware_args:
        if middleware_name not in _nameToMiddleware:
            if logger is not None:
                logger.warning(f"middleware {repr(middleware_name)} not defined, all middleware defined are {repr(list(_nameToMiddleware.keys()))}")
        try:
            middleware_cls, middleware_args_cls = _nameToMiddleware[middleware_name]
            middleware_list.append(middleware_cls(middleware_args_cls(middleware_args[middleware_name])))
        except Exception as e:
            if logger is not None:
                error_report = f'[{repr(type(e).__name__)}] {repr(e)}'
                logger.warning(f"failed to initialize middleware {repr(middleware_name)} with args {repr(middleware_args[middleware_name])}, caught error {error_report}")
            raise e
    return middleware_list


def _module_postprocess():
    module_report = {}
    for var_name, var_value in globals().items():
        if var_name in __all__ and isinstance(var_value, type):
            module_report[repr(var_value.__qualname__)] = {name: repr(setter) for name, setter in var_value._defined_args.items()}
    logger.debug(f"module {__name__} loaded:\n{json.dumps(module_report, indent=4, ensure_ascii=False)}\n")
    module_ref_path = 'docs/refs'
    if not os.path.exists(module_ref_path):
        os.makedirs(module_ref_path)
    with open(os.path.join(module_ref_path, f'{__name__}.json'), 'w') as f:
        json.dump(module_report, f, indent=4, ensure_ascii=False)


_module_postprocess()

logger.info(f"module {__name__} imported")