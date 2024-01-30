import os
import time
import datetime
import traceback
from typing import Any, List, Optional
from multiprocessing import Process

from ..args.arg_group import RequestorArgs
from ..utils.ds import AttrDict
from ..utils.log import get_logger
from ..utils.cls import RootType
from ..utils.defs import (
    FINISHED,
    FAILED,
    RFC_GLOBAL_MANAGER,
)
from ..utils.func import load_object
from ..item.queue import RootQueue
# from ..item.item import Item  # for circular import issue we cannot import `Item` for typing

from .session import Session
from .middleware import Middleware

logger = get_logger(__name__)
logger.info(f"importing module {__name__}")

try:
    import trio
except Exception as e:
    error_report = f'[{repr(type(e).__name__)}] {repr(e)}'
    logger.warning(f"failed to import trio, caught error {error_report}")
    trio = None

try:
    import asyncio
except Exception as e:
    error_report = f'[{repr(type(e).__name__)}] {repr(e)}'
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
    _name: str = 'requestor'
    
    _defined_args = {
        'nproc': 1,
        'async_sema': 1,
        'report_step': 100,
        'wait_timeout': 20,
        'wait_sleep': 2,
    }

    def __init__(
        self,
        session: Session,
        middleware: List[Middleware],
        requestor_args: RequestorArgs,
    ):
        super().__init__(requestor_args)
        self._get_logger_self(__name__, add_file_handler=True, level='info')  # if loggers in multiprocessing intervening with each other, we will add special file handler for multiprocessing manually
        self._session = session
        self._middleware = middleware
        self._failed_items = []
        self._finished_items = []
        self._step = 0
        self._log_dir = 'logs'
        if os.path.exists(os.path.join(self._log_dir, 'items_finished.txt')):
            os.remove(os.path.join(self._log_dir, 'items_finished.txt'))
        if os.path.exists(os.path.join(self._log_dir, 'items_failed.txt')):
            os.remove(os.path.join(self._log_dir, 'items_failed.txt'))

    def _handle_error(
        self,
        error: Exception,
        item,
        result: Any,
    ):
        error_report = f'[{repr(type(error).__name__)}] {repr(error)}'
        self._failed_items.append((repr(item), error_report, item._timestamp[FAILED]))
        item._logger.error(f"failed on {repr(item)}, caught error {repr(error_report)}")
        item._logger.error(traceback.format_exc())
        self._logger.warning(f"failed on {repr(item)}, caught error {repr(error_report)}")
    
    def _get_item_from_root_queue(
        self,
    ):
        return RootQueue.fetch()
    
    def _check_saved_result(
        self,
        item,
    ):
        if not os.path.exists(os.path.join(item.save_dir, '_result.pkl')):
            return None
        try:
            self._logger.info(f"process {self._logger._process_name} saved result found for {repr(item)}")
            item._logger.info(f"saved result found for {repr(item)}")
            return load_object(os.path.join(item.save_dir, '_result.pkl'), raise_exception=True, logger=self._logger)
        except Exception as e:
            error_report = f'[{repr(type(e).__name__)}] {repr(e)}\n{traceback.format_exc()}'
            self._logger.info(f"process {self._logger._process_name} failed to load saved result for {repr(item)}, caught error {repr(error_report)}")
            item._logger.info(f"failed to load saved result for {repr(item)}, caught error {repr(error_report)}")
            return None
        
    def _fetch_single_finally_sync(
        self,
    ):
        self._step += 1
        if self._step % self.report_step == 0:
            self._report_items()
            
    def _fetch_single_sync(
        self,
        item,
    ):
        item.process()
        result = self._check_saved_result(item)
        if result is not None:
            item.finish(True, result)
            self._finished_items.append((repr(item), 'SKIPPED', item._timestamp[FINISHED]))
            self._logger.info(f"process {self._logger._process_name} fetched {repr(item)} from saved result")
            self._fetch_single_finally_sync()
            return
        try:
            resp = self._session.request(item)
            result = AttrDict({
                'response': resp,
            })
            for middleware in self._middleware:
                result = middleware.apply_sync(item, result, self._session._request_lib)
            item.finish(True, result)
            self._finished_items.append((repr(item), 'OK', item._timestamp[FINISHED]))
            self._logger.info(f"process {self._logger._process_name} fetched {repr(item)}")
        except Exception as e:
            self._logger.warning(f"process {self._logger._process_name} failed on {repr(item)}, caught error {repr(e)}")
            item.finish(False)
            self._handle_error(e, item, result)
        finally:
            self._fetch_single_finally_sync()
            
    async def _fetch_single_finally_async(
        self,
        sema,
    ):
        self._step += 1
        if self._step % self.report_step == 0:
            self._report_items()
        if sema is not None:
            sema.release()
    
    async def _fetch_single_async(
        self,
        item,
        sema: Any = None,
        task_name: str = None,
    ):
        item.process()
        result = self._check_saved_result(item)
        if result is not None:
            item.finish(True, result)
            self._finished_items.append((repr(item), 'SKIPPED', item._timestamp[FINISHED]))
            self._logger.info(f"process {self._logger._process_name} task {task_name} fetched {repr(item)} from saved result")
            await self._fetch_single_finally_async(sema)
            return
        try:
            resp = await self._session.request(item)
            result = AttrDict({
                'response': resp,
            })
            for middleware in self._middleware:
                result = await middleware.apply_async(item, result, self._session._request_lib, self._session._async_lib)
            item.finish(True, result)
            self._finished_items.append((repr(item), 'OK', item._timestamp[FINISHED]))
            self._logger.info(f"process {self._logger._process_name} task {task_name} fetched {repr(item)}, step {self._step}")
        except Exception as e:
            self._logger.warning(f"process {self._logger._process_name} task {task_name} failed on {repr(item)}, step {self._step}, caught error {repr(e)}\n{traceback.format_exc()}")
            # self._logger.warning(f"process {self._logger._process_name} task {task_name} failed on {repr(item)}, step {self._step}, caught error {repr(e)}")
            item.finish(False)
            self._handle_error(e, item, result)
        finally:
            await self._fetch_single_finally_async(sema)

    def _fetch_all_sync(
        self,
    ):
        st_wait_time = None
        while True:
            item = self._get_item_from_root_queue()
            if item is None:
                if st_wait_time is None:
                    st_wait_time = time.time()
                if time.time() - st_wait_time > self.wait_timeout:
                    self._logger.info(f"process {self._logger._process_name} got None from root queue, and waited for {self.wait_timeout} seconds, QUIT")
                    break
                time.sleep(self.wait_sleep)
                continue
            st_wait_time = None
            self._logger.info(f"process {self._logger._process_name} got {repr(item)} from root queue")
            self._fetch_single_sync(item)
        self._finish_sync()

    async def _fetch_all_asyncio(
        self,
        async_sema: int,
    ):
        sema = asyncio.Semaphore(async_sema)
        tasks = []
        st_wait_time = None
        while True:
            item = self._get_item_from_root_queue()
            if item is None:
                if st_wait_time is None:
                    st_wait_time = time.time()
                if time.time() - st_wait_time > self.wait_timeout:
                    self._logger.info(f"process {self._logger._process_name} got None from root queue, and waited for {self.wait_timeout} seconds, QUIT")
                    break
                await asyncio.sleep(self.wait_sleep)
                continue
            st_wait_time = None
            self._logger.info(f"process {self._logger._process_name} got {repr(item)} from root queue")
            await sema.acquire()
            task_name = f'async-{len(tasks)}'
            tasks.append(asyncio.create_task(self._fetch_single_async(item, sema, task_name), name=task_name))
        for task in tasks:
            await task
        await self._finish_async()
    
    async def _fetch_all_trio(
        self,
        async_sema: int,
    ):
        sema = trio.Semaphore(async_sema, max_value=async_sema)
        st_wait_time = None
        async with trio.open_nursery() as nursery:
            while True:
                item = self._get_item_from_root_queue()
                if item is None:
                    if st_wait_time is None:
                        st_wait_time = time.time()
                    if time.time() - st_wait_time > self.wait_timeout:
                        self._logger.info(f"process {self._logger._process_name} got None from root queue, and waited for {self.wait_timeout} seconds, QUIT")
                        break
                    time.sleep(self.wait_sleep)  # TODO
                    continue
                st_wait_time = None
                self._logger.info(f"process {self._logger._process_name} got {repr(item)} from root queue")
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
            self._logger.info(f"process {self._logger._process_name} start fetching with sync")
            self._fetch_all_sync()
        else:
            if self._session._async_lib == 'asyncio':
                if asyncio is None:
                    raise ValueError(f"async_lib {repr(self._session._async_lib)} is not supported in this environment")
                self._logger.info(f"process {process_name} start fetching with asyncio")
                asyncio.run(self._fetch_all_asyncio(async_sema=async_sema))
            elif self._session._async_lib == 'trio':
                if trio is None:
                    raise ValueError(f"async_lib {repr(self._session._async_lib)} is not supported in this environment")
                self._logger.info(f"process {process_name} start fetching with trio")
                trio.run(self._fetch_all_trio, async_sema)
            else:
                raise ValueError(f"unsupported async_lib {repr(self._session._async_lib)}")
              
    def _report_items(
        self,
    ):
        with open('logs/items_finished.txt', 'a') as f:
            f.write('\n'.join([f'{item}\n\tstatus: {error}\ntimestamp: {datetime.datetime.fromtimestamp(time)}\n' for item, error, time in self._finished_items])+'\n')
            self._finished_items = []
        with open('logs/items_failed.txt', 'a') as f:
            f.write('\n'.join([f'{item}\n\tstatus: {error}\ntimestamp: {datetime.datetime.fromtimestamp(time)}\n' for item, error, time in self._failed_items])+'\n')
            self._failed_items = []
        
    def _finish_sync(
        self,
    ):
        self._report_items()
        self._session.close()
        
    
    async def _finish_async(
        self,
    ):
        self._report_items()
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
        self._logger.info(f"start fetching with {nproc} processes and {async_sema} async semaphores")
        processes = []
        for i in range(nproc):
            process_name = f'requestor-worker-{i}'
            processes.append(Process(target=self._fetch_all_single_process, args=(async_sema, process_name), name=process_name))
            processes[i].start()
        for i in range(nproc):
            processes[i].join()
    
    def __repr__(self):
        cls_repr = f'{repr(self.__class__.__qualname__)}'
        args_repr = repr({args: self[args] for args in self._defined_args})
        return f'{cls_repr}({args_repr})'
        


# ------------------------------------ Module Postprocess ------------------------------------ #

logger.info(f"module {__name__} imported")