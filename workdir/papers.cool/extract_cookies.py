import os
import json
import asyncio
import aiohttp
from tqdm import tqdm
import multiprocessing as mp


savepath = 'cookies/'


async def extract_cookies_single_task(id, n_reqs, sema):
    # print('C', flush=True)
    cookies = []
    for i in range(n_reqs):
        try:
            # async with aiohttp.request('get', "https://papers.cool", proxy='http://10.176.52.116:7890') as resp:
            #     cookies.append({'client_id': dict(resp.cookies)['client_id'].value})
            async with aiohttp.request('post', "https://papers.cool/venue/star?key=kimi&paper=P16-1019@ACL", proxy='http://10.176.52.116:7890') as resp:
                cookies.append({'client_id': dict(resp.cookies)['client_id'].value})
                # print(f'extracted one cookies, id {id}', flush=True)
        except Exception as e:
            # raise e
            continue
    # json.dump(cookies, open(os.path.join(savepath, f'cookies_{id}.json'), 'w'), indent=4)
    print(f'extracted {len(cookies)} cookies for id {id}', flush=True)
    sema.release()
    return cookies


async def extract_cookies_single_async(id, n_task, n_reqs, n_sema):
    # print('B', flush=True)
    sema = asyncio.Semaphore(n_sema)
    tasks = []
    for i in range(n_task):
        await sema.acquire()
        tasks.append(asyncio.create_task(extract_cookies_single_task(id+'.'+str(i), n_reqs, sema)))
    results = []
    for task in tasks:
        result = await task
        results += result   
    # json.dump(results, open(os.path.join(savepath, f'cookies_{id}.json'), 'w'), indent=4)
    print(f'extracted {len(results)} cookies for id {id}', flush=True)
    return results


def extract_cookies_single(id, n_task, n_reqs, n_sema):
    # print('A', flush=True)
    return asyncio.run(extract_cookies_single_async(id, n_task, n_reqs, n_sema))


def extract_cookies(n_runs, n_proc, n_task, n_reqs, n_sema):
    os.makedirs(savepath, exist_ok=True)
    with mp.Pool(n_proc) as pool:
        results = pool.starmap(extract_cookies_single, [(str(id), n_task, n_reqs, n_sema) for id in range(n_runs)])
    json.dump(results, open(os.path.join(savepath, 'cookies.json'), 'w'), indent=4)
    return results


def merge_cookies_to_json_file():
    cookies = json.load(open(os.path.join(savepath, 'cookies.json'), 'r'))
    result = []
    for block in cookies:
        for item in block:
            assert 'client_id' in item
            result.append(item['client_id'])
    json.dump(result, open('cookies.json', 'w'), indent=4)
    return result


extract_cookies(
    n_runs=10,
    n_proc=24,
    n_task=100,
    n_sema=24,
    n_reqs=10,
)
merge_cookies_to_json_file()