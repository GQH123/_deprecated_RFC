import os
from multiprocessing import process
from multiprocessing.managers import SyncManager

def fetch():
    print(os.getpid())

SyncManager.register('fetch', callable=fetch)
manager = SyncManager()
manager.start()

print(os.getpid())
x = [1, 2, 3, 4, []]
y = manager.list(x)
print(id(x), id(x[-1]), id(y), id(y[-1]))
print(type(x), type(y), type(x[-1]), type(y[-1]))
print(x, x[-1], y, y[-1])
y[-1].append(5)
print(x, x[-1], y, y[-1])
y.append(5)
print(x, x[-1], y, y[-1])
x[-1].append(6)
print(x, x[-1], y, y[-1])
manager.fetch()