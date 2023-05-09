import time
import trio
import asyncio
import inspect
import functools
import traceback
from typing import Any

from RFC.itemset.RawItemset import RawItemset, RawItem
from RFC.utils.BaseModule import BaseModule
from RFC.utils.exception_utils import NotSupported, ConditionOverflowError, ParamValueError
from RFC.utils.functional_utils import get_prev_module_name, log, update_output_channels, save_object

from .session.session import get_session
from .BaseRequestorConfig import BaseRequestorConfig


all_supported_async_frameworks = ['trio', 'asyncio']


def retrying(retry_times:int|str='forever', sleep_time=1, **kwargs):  # used only in manager class
    if retry_times == 'forever':
        retry_times = -1
    elif isinstance(retry_times, int):
        if retry_times < 0:
            retry_times = -1
    else:
        raise ParamValueError('retry_times', retry_times, ['forever'], get_prev_module_name(1))

    note = kwargs.get('note', 'Retrying')
    mode = kwargs.get('mode', 'warning')
    from_module = kwargs.get('from_module', get_prev_module_name(1))
    async_framework = kwargs.get('async_framework', None)

    def returned_func(func):
        @functools.wraps(func)
        async def wrapped_async_func(*args, **kwargs):
            nonlocal retry_times
            while retry_times != 0:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    log(message=f'retrying({retry_times}), <{type(e)}> {e}', file='current_requested_item_log', note=note, mode=mode, from_module=from_module)
                    retry_times = retry_times-1 if retry_times > 0 else retry_times
                    await async_framework.sleep(sleep_time)
        return wrapped_async_func
    return returned_func


class BaseRequestor(BaseModule):
    def _init_session(self, requestor_config):
        self.session_config = requestor_config.session_config
        self.session = get_session(self.session_config)
        self.framework = self.session.framework
        self.use_async = self.session.use_async
        if self.use_async:
            self.async_framework = self.session.async_framework
            if self.async_framework not in all_supported_async_frameworks:
                raise NotSupported('self.async_framework', self.async_framework, all_supported_async_frameworks, __name__)
            if self.async_framework == 'trio':
                self._fetch = retrying(async_framework=trio)(self._fetch)
            elif self.async_framework == 'asyncio':
                self._fetch = retrying(async_framework=asyncio)(self._fetch)
        else:
            self.async_framework = None

    def _init_all(self, requestor_config):
        self._init_session(requestor_config)

    def __init__(
        self,
        requestor_config: BaseRequestorConfig,
    ):
        super().__init__(requestor_config)
        self._init_all(requestor_config)
    
    def _save_result(
        self,
        name: str,
        result: Any,
    ):
        save_object(result, name, 'result')

    def _error_handler(
        self,
        e: Exception,
        item: RawItem,
        name: str = None,
    ):
        if name is None:
            name = f'{item.name}'
        log(f'Error fetching {name}: {e}\n', 'main', 'Requestor.Error', 'error', __name__)
        log(f'Error fetching {name}: {e}, traceback:\n{traceback.format_exc()}\n', 'debug', 'Requestor.Error', 'error', __name__)
        log(f'Error fetching {name}: {e}\n', 'test', 'Requestor.Error', 'error', __name__)

    async def _fetch(
        self,
        rank: int,
        item: RawItem,
        sema: Any = None,
        name: str = None,
    ):
        try:
            update_output_channels('current_requested_item_log', f'{item.name}.log', 'log')
            result = await self.session.request(item, item.return_type, rank)
            self._save_result(item.name, result)
        except Exception as e:
            self._error_handler(e, item, name)
        if sema is not None:
            sema.release()

    async def _fetch_all_trio(
        self,
        rank: int,
        items: RawItemset,
        async_sema: int = 1,
    ):
        sema = trio.Semaphore(async_sema, max_value=async_sema)
        async with trio.open_nursery() as nursery:
            for item in items:
                await sema.acquire()
                nursery.start_soon(self._fetch, rank, item, item.return_type, sema, f'fetching {item.name}')

    async def _fetch_all_asyncio(
        self,
        rank: int,
        items: RawItemset,
        async_sema: int = 1,
    ):
        sema = asyncio.Semaphore(async_sema)
        tasks = []
        for item in items:
            await sema.acquire()
            tasks.append(asyncio.create_task(self._fetch(rank, item, item.return_type, sema, f'fetching {item.name}')))
        for task in tasks:
            await task

    async def _fetch_all_sync(
        self,
        rank: int,
        items: RawItemset,
    ):
        for item in items:
            await self._fetch(rank, item, None, f'fetching {item.name}')

    def run_single(
        self,
        items: RawItemset,
        rank = 0,
        nproc: int = 1,
        async_sema: int = 1,
    ):
        if self.use_async:
            if self.async_framework == 'trio':
                trio.run(self._fetch_all_trio, rank, items, async_sema)
            elif self.async_framework == 'asyncio':
                asyncio.run(self._fetch_all_asyncio(rank, items, async_sema))
            else:
                raise ConditionOverflowError(self.async_framework,  __name__)
        else:
            asyncio.run(self._fetch_all_sync(rank, items))
    
    def run(
        self,
        items: RawItemset,
        nproc: int = 1,
        async_sema: int = 1,
    ):
        self.run_single(items, 0, nproc, async_sema)
    
    def _retrieve_config(
        self,
        return_config: bool = False
    ):
        parent_attr = super()._retrieve_config()
        my_attr = parent_attr
        my_attr.update({
            'session_config': self.session.__config__(),
        })
        if return_config:
            return BaseRequestorConfig(**my_attr)
        else:
            return my_attr