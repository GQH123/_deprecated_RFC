from typing import Any, List, Optional
from multiprocessing import Process

from ..args.arg_group import RequestorArgs
from ..utils.ds import AttrDict
from ..utils.log import get_logger
from ..utils.cls import RootType
from ..item.item import Item, ItemType

from .session import Session
from .middleware import Middleware

logger = get_logger(__name__)

try:
    import trio
except Exception as e:
    error_report = f'[{repr(e).__name__}] {repr(e)}'
    logger.warning(f"failed to import trio, caught error {error_report}")
    trio = None

try:
    import asyncio
except Exception as e:
    error_report = f'[{repr(e).__name__}] {repr(e)}'
    logger.warning(f"failed to import asyncio, caught error {error_report}")
    asyncio = None

__all__ = [
    'Requestor'
]


class Requestor(AttrDict, RootType):
    """
        Requestor bridges `Item`s, `Session`s and `MiddleWare`s, to perform complete life-cycle of requesting an item.
        
        It supportes both sync/async request libs, and can be run in single/multiple processes.
        
        It is not expected to be subclassed.
    """
    def __init__(
        self,
        session: Session,
        middleware: List[Middleware],
        requestor_args: RequestorArgs,
    ):
        super().__init__(requestor_args)
        self._get_logger(add_file_handler=True)  # if loggers in multiprocessing intervening with each other, we will add special file handler for multiprocessing manually
        self._session = session
        self._middleware = middleware

    def _handle_error(
        self,
        error: Exception,
        item: Item,
        result: Any,
    ):
        # TODO: add error handling logics
        raise error
    
    def _get_item_from_root_queue(
        self,
    ):
        return ItemType.fetch()
    
    def _fetch_single_sync(
        self,
        item: Item,
    ):
        item.process()
        result = None
        try:
            result = self._session.request(item)
            for middleware in self._middleware:
                result, status = middleware.apply_sync(item, result, self._session._request_lib, self._session._async_lib)
            item.finish(True, result)
            self._logger.info(f"{repr(self)} process {self._logger._process_name} fetched {repr(item)}")
        except Exception as e:
            self._logger.info(f"{repr(self)} process {self._logger._process_name} failed on {repr(item)}, caught error {repr(e)}")
            item.finish(False)
            self._handle_error(e, item, result)
    
    async def _fetch_single_async(
        self,
        item: Item,
        sema: Any = None,
    ):
        item.process()
        result = None
        try:
            result = await self._session.request(item)
            for middleware in self._middleware:
                result, status = await middleware.apply_async(item, result)
            item.finish(True, result)
            self._logger.info(f"{repr(self)} process {self._logger._process_name} fetched {repr(item)}")
        except Exception as e:
            self._logger.info(f"{repr(self)} process {self._logger._process_name} failed on {repr(item)}, caught error {repr(e)}")
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
            self._logger.info(f"{repr(self)} process {self._logger._process_name} got {repr(item)} from root queue")
            if item is None:
                break
            self._fetch_single_sync(item)
        self._finish_sync()

    async def _fetch_all_asyncio(
        self,
        async_sema: int,
    ):
        sema = asyncio.Semaphore(async_sema)
        tasks = []
        while True:
            item = self._get_item_from_root_queue()
            self._logger.info(f"{repr(self)} process {self._logger._process_name} got {repr(item)} from root queue")
            if item is None:
                break
            await sema.acquire()
            tasks.append(asyncio.create_task(self._fetch_single_async(item, sema)))
        for task in tasks:
            await task
        await self._finish_async()
    
    async def _fetch_all_trio(
        self,
        async_sema: int,
    ):
        sema = trio.Semaphore(async_sema, max_value=async_sema)
        async with trio.open_nursery() as nursery:
            while True:
                item = self._get_item_from_root_queue()
                self._logger.info(f"{repr(self)} process {self._logger._process_name} got {repr(item)} from root queue")
                if item is None:
                    break
                await sema.acquire()
                nursery.start_soon(self._fetch_single_async, item, sema)
        await self._finish_async()
        
    def _fetch_all_single_process(
        self,
        async_sema: int,
        process_name: str = 'none',
    ):
        """
            Requestor now in different processes, each process has its own context.
        """
        self._logger._process_name = process_name
        if self._session._async_lib == 'none':
            self._logger.info(f"{repr(self)} process {process_name} start fetching with sync")
            self._fetch_all_sync()
        else:
            if self._session._async_lib == 'asyncio':
                if asyncio is None:
                    raise ValueError(f"async_lib {repr(self._session._async_lib)} is not supported in this environment")
                self._logger.info(f"{repr(self)} process {process_name} start fetching with asyncio")
                asyncio.run(self._fetch_all_asyncio(async_sema=async_sema))
            elif self._session._async_lib == 'trio':
                if trio is None:
                    raise ValueError(f"async_lib {repr(self._session._async_lib)} is not supported in this environment")
                self._logger.info(f"{repr(self)} process {process_name} start fetching with trio")
                trio.run(self._fetch_all_trio, async_sema)
            else:
                raise ValueError(f"unsupported async_lib {repr(self._session._async_lib)} in {repr(self)}")
        
    def _finish_sync(
        self,
    ):
        self._session.close()
    
    async def _finish_async(
        self,
    ):
        await self._session.close()
    
    def run(
        self,
        nproc: Optional[int] = None,
        async_sema: Optional[int] = None,
    ):
        if nproc is None:
            nproc = self.nproc
        if async_sema is None:
            async_sema = self.async_sema
        async_sema = async_sema if self._session._async_lib != 'none' else None
        self._logger.info(f"{repr(self)} start fetching with {nproc} processes and {async_sema} async semaphores")
        processes = []
        for i in range(nproc):
            process_name = f'requestor-worker-{i}'
            processes.append(Process(target=self._fetch_all_single_process, args=(async_sema, process_name), name=process_name))
            processes[i].start()
        for i in range(nproc):
            processes[i].join()