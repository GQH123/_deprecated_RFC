from _queue import add, pop, mp


def run(lock, _queue):
    global x
    x = [13]
    a = pop(lock, _queue)
    a.f()
    a = pop(lock, _queue)
    a.f()