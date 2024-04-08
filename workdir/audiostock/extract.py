import os
import json


def _parse_exception_type(exception, item_id):
    if 'ClientHttpProxyError' in exception:
        return 'ClientHttpProxyError'
    if 'ClientConnectorError' in exception:
        return 'ClientConnectorError'
    if 'ClientConnectorSSLError' in exception:
        return 'ClientConnectorSSLError'
    if 'unexpected status code 404' in exception:
        return 'StatusCode 404 Error'
    if 'TimeoutError' in exception:
        return 'TimeoutError'
    if 'ClientProxyConnectionError' in exception:
        return 'ClientProxyConnectionError'
    if 'ClientConnectorCertificateError' in exception:
        return 'ClientConnectorCertificateError'
    if 'ClientOSError' in exception:
        return 'ClientOSError'
    if 'unexpected status code 403' in exception:
        return 'StatusCode 403 Error'
    if 'unexpected status code 502' in exception:
        return 'StatusCode 502 Error'
    if 'unexpected status code 500' in exception:
        return 'StatusCode 500 Error'
    if 'ServerDisconnectedError' in exception:
        return 'ServerDisconnectedError'
    if 'ClientPayloadError' in exception:
        return 'ClientPayloadError'
    exception = exception.strip()
    return exception.replace(item_id, '')


def _parse_status_type(status, item_id):
    if 'SKIPPED' in status:
        return 'SKIPPED'
    if 'OK' in status:
        return 'OK'
    status = status.strip()
    return status.replace(item_id, '')


def extract_fail_exceptions(with_id=False, savepath=None, show=True):
    with open('logs/items_failed.txt', 'r') as f:
        failed_items = f.read().split('\n\n')
    exception_set = {}
    for item in failed_items:
        if not item:
            continue
        item_id, exception, timestamp = item.split('\n')
        exception = exception.strip()
        item_type = item_id.split('.')[-1].split('(')[0]
        item_id_number = item_id.split('(')[-1].split(')')[0]
        exception_type = _parse_exception_type(exception, item_id)
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
        

def extract_finished_status(with_id=False, savepath=None, show=True):
    with open('logs/items_finished.txt', 'r') as f:
        failed_items = f.read().split('\n\n')
    status_set = {}
    for item in failed_items:
        if not item:
            continue
        item_id, status, timestamp = item.split('\n')
        status = status.strip()
        item_type = item_id.split('.')[-1].split('(')[0]
        item_id_number = item_id.split('(')[-1].split(')')[0]
        status_type = _parse_status_type(status, item_id)
        if status_type not in status_set:
            status_set[status_type] = {}
            status_set[status_type]['total'] = 0
            status_set[status_type]['type'] = {}
        status_set[status_type]['total'] += 1
        if with_id:
            status_set[status_type]['type'][item_type] = status_set[status_type]['type'].get(item_type, [])
            status_set[status_type]['type'][item_type].append(item_id_number)
        else:
            status_set[status_type]['type'][item_type] = status_set[status_type]['type'].get(item_type, 0) + 1
    if show and not with_id:
        print(json.dumps(status_set, indent=4, ensure_ascii=False))
    if savepath:
        json.dump(status_set, open(savepath, 'w'), indent=4, ensure_ascii=False)


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
    

def extract_saves():
    ...


extract_fail_exceptions(with_id=True, savepath='saved_logs/statistics_failed_exceptions_details.json')
extract_fail_exceptions(with_id=False, savepath='saved_logs/statistics_failed_exceptions.json')
extract_finished_status(with_id=True, savepath='saved_logs/statistics_finished_status_details.json')
extract_finished_status(with_id=False, savepath='saved_logs/statistics_finished_status.json')
extract_counts()