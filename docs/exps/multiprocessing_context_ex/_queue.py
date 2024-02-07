import multiprocessing as mp


def add(x, lock, _queue):
    with lock:
        _queue.append(x)
        
        
def pop(lock, _queue):
    with lock:
        return _queue.pop()