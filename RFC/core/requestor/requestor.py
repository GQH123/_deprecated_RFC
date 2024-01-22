from typing import Any

from RFC.core.utils.cls import RootType
from RFC.core.item.item import Item

from .session import Session
from .middlewares import get_middlewares

import trio
import asyncio


class Requestor(RootType):
    def __init__(
        self,
        session: Session,
    ):
        super().__init__()
        self._get_logger()
        self._session = session
        # self._request_lib = session._request_lib
        self._async_lib = session._async_lib
    
    def _handle_error(
        self,
        error: Exception,
        item: Item,
        result: Any,
    ):
        ...
        raise error
    
    def _get_item_from_root_queue(
        self,
    ):
        ...
    
    def _fetch_single(
        self,
        item: Item,
    ):
        item.process()
        middlewares = get_middlewares(item.middlewares)
        result = None
        try:
            result = self._session.request(item)
            for middleware in middlewares:
                result, status = middleware(item, result)
            item.finish(True, result)
            self._logger.info(f'fetched {repr(item)}')
        except Exception as e:
            item.finish(False)
            self._handle_error(e, item, result)
    
    async def _fetch_single_async(
        self,
        item: Item,
        sema: Any = None,
    ):
        item.process()
        middlewares = get_middlewares(item.middlewares)
        result = None
        try:
            result = await self._session.request_async(item)
            for middleware in middlewares:
                result, status = middleware(item, result)
            item.finish(True, result)
            self._logger.info(f'fetched {repr(item)}')
        except Exception as e:
            item.finish(False)
            self._handle_error(e, item, result)
        finally:
            if sema is not None:
                sema.release()

    def _fetch_all_sync(
        self,
    ):
        while True:
            item = self._get_item_from_root_queue()
            if item is None:
                break
            self._fetch_single(item)
        self._finish()

    async def _fetch_all_asyncio(
        self,
        async_sema: int = 1,
    ):
        sema = asyncio.Semaphore(async_sema)
        tasks = []
        while True:
            item = self._get_item_from_root_queue()
            if item is None:
                break
            await sema.acquire()
            tasks.append(asyncio.create_task(self._fetch_single_async(item, sema)))
        for task in tasks:
            await task
        await self._finish_async()
    
    async def _fetch_all_trio(
        self,
        async_sema: int = 1,
    ):
        sema = trio.Semaphore(async_sema, max_value=async_sema)
        async with trio.open_nursery() as nursery:
            while True:
                item = self._get_item_from_root_queue()
                if item is None:
                    break
                await sema.acquire()
                nursery.start_soon(self._fetch_single_async, item, sema)
        await self._finish_async()
        
    def _fetch_all_single_process(
        self,
        async_sema: int = 1,
    ):
        if self._async_lib is None or self._async_lib == 'none':
            self._fetch_all_sync()
        else:
            if self._async_lib == 'asyncio':
                asyncio.run(self._fetch_all_asyncio(async_sema=async_sema))
            elif self._async_lib == 'trio':
                trio.run(self._fetch_all_trio, async_sema=async_sema)
            else:
                raise ValueError(f'unsupported async_lib {repr(self._async_lib)} in {repr(self)}')
        
    def _finish(
        self,
    ):
        self._session.close()
    
    async def _finish_async(
        self,
    ):
        await self._session.close_async()
    
    def fetch(
        self,
        nproc: int = 1,
        async_sema: int = 1,
    ):
        # TODO: add multiprocessing support
        self._fetch_all_single_process(async_sema=async_sema)