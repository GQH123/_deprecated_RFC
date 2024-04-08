import os
import json
from tqdm import tqdm


def extract_fail_exceptions(with_id=False, savepath=None, show=True):
    with open('logs/items_failed.txt', 'r') as f:
        failed_items = f.read().split('\n\n')
    exception_set = {}
    for item in failed_items:
        if not item:
            continue
        item_id, exception, timestamp = item.split('\n')
        item_type = item_id.split('.')[-1].split('(')[0]
        item_id_number = item_id.split('(')[-1].split(')')[0]
        exception = exception.strip()
        exception_type = exception.replace(item_id, '')
        if exception_type not in exception_set:
            exception_set[exception_type] = {}
            exception_set[exception_type]['total'] = 0
            exception_set[exception_type]['type'] = {}
        exception_set[exception_type]['total'] += 1
        if with_id:
            exception_set[exception_type]['type'][item_type] = exception_set[exception_type]['type'].get(item_type, [])
            exception_set[exception_type]['type'][item_type].append(item_id_number)
        else:
            exception_set[exception_type]['type'][item_type] = exception_set[exception_type]['type'].get(item_type, 0) + 1
    if show and not with_id:
        print(json.dumps(exception_set, indent=4, ensure_ascii=False))
    if savepath:
        json.dump(exception_set, open(savepath, 'w'), indent=4, ensure_ascii=False)


def extract_counts():
    count = {}
    with open('logs/items_failed.txt', 'r') as f:
        failed_items = [item for item in f.read().split('\n\n') if item]
    count['failed'] = {}
    count['failed']['total'] = len(failed_items)
    count['failed']['type'] = {}
    for item in failed_items:
        if not item:
            continue
        item_id, exception, timestamp = item.split('\n')
        exception = exception.strip()
        item_type = item_id.split('.')[-1].split('(')[0]
        count['failed']['type'][item_type] = count['failed']['type'].get(item_type, 0) + 1
    with open('logs/items_finished.txt', 'r') as f:
        finished_items = [item for item in f.read().split('\n\n') if item]
    count['finished'] = {}
    count['finished']['total'] = len(finished_items)
    count['finished']['type'] = {}
    for item in finished_items:
        if not item:
            continue
        item_id, status, timestamp = item.split('\n')
        item_type = item_id.split('.')[-1].split('(')[0]
        count['finished']['type'][item_type] = count['finished']['type'].get(item_type, 0) + 1
    print(json.dumps(count, indent=4, ensure_ascii=False))


# extract_fail_exceptions(with_id=True, savepath='logs/exceptions.json')
# extract_fail_exceptions()
# extract_counts()