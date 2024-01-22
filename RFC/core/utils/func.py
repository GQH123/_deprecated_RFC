import functools


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