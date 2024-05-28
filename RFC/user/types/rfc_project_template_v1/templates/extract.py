import os
import re
import json


def _parse_status_type(status, msg, extract_type, item_id):
    if extract_type == 'failed':
        if status == 'ValueError' and 'unexpected status code' in msg:
            return f"StatusCode {msg.split('unexpected status code ')[1].split(' ')[0]} Error"
    elif extract_type == 'finished':
        pass
    else:
        pass
    return status.strip()


def extract_status(extract_type, with_id=False, savedir=None, show=True):
    logpath = f'logs/items_{extract_type}.txt'
    status_re_switch = {
        'failed': 'status: \[\'([^\[\]]+)\'\](.*)$',
        'finished': 'status: ([A-Za-z0-9_]+)()$'
    }
    if extract_type not in status_re_switch:
        raise ValueError(f'invalid type: {extract_type}, should be one of {status_re_switch.keys()}')
    savefile = f'statistics_{extract_type}_status'
    if with_id:
        savefile += '_details'
    savefile += '.json'
    
    with open(logpath, 'r') as f:
        failed_items = f.read().split('\n\n')
    status_set = {}
    all_status_id = {}
    for item in failed_items:
        if not item:
            continue
        item_id, status, timestamp = item.split('\n')
        status = status.strip()
        status_match = re.findall(status_re_switch[extract_type], status)
        assert len(status_match) == 1
        status_type, status_msg = status_match[0]
        item_match = re.findall('(?:[^()]+\(.+\)\.)*([^()]+)\((.+)\)$', item_id)
        assert len(item_match) == 1
        item_type, item_id_number = item_match[0]
        status_type = _parse_status_type(status_type, status_msg, extract_type, item_id)
        if status_type not in status_set:
            status_set[status_type] = {}
            status_set[status_type]['total'] = 0
            status_set[status_type]['type'] = {}
        status_set[status_type]['total'] += 1
        if with_id:
            status_set[status_type]['type'][item_type] = status_set[status_type]['type'].get(item_type, [])
            status_set[status_type]['type'][item_type].append(item_id_number)
            all_status_id[item_type] = all_status_id.get(item_type, [])
            all_status_id[item_type].append(item_id_number)
        else:
            status_set[status_type]['type'][item_type] = status_set[status_type]['type'].get(item_type, 0) + 1
    if show and not with_id:
        print(json.dumps(status_set, indent=4, ensure_ascii=False))
    if with_id:
        first = True
        for item_type in all_status_id:
            all_status_id_count = {}
            for item_id in all_status_id[item_type]:
                all_status_id_count[item_id] = all_status_id_count.get(item_id, 0) + 1
            for item_id, count in all_status_id_count.items():
                if count > 1:
                    if first:
                        print('duplicated item_id:')
                        first = False
                    print(item_id, count)
        status_set['__all__'] = all_status_id
        print()
    if savedir:
        json.dump(status_set, open(os.path.join(savedir, savefile), 'w'), indent=4, ensure_ascii=False)


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
    

extract_status('failed', with_id=False, savedir='saved_logs')
extract_status('failed', with_id=True, savedir='saved_logs')
extract_status('finished', with_id=False, savedir='saved_logs')
extract_status('finished', with_id=True, savedir='saved_logs')
# extract_counts()