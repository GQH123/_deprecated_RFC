from _queue import mp
from A import test_1, test_2
from A2 import test_2 as _test_2
from B import run

manager = mp.Manager()
lock = manager.RLock()
_queue = manager.list()



p1 = mp.Process(target=test_2, args=(lock, _queue))
p1.start()
p1.join()
# p1 = mp.Process(target=_test_2, args=(lock, _queue))
# p1.start()
# p1.join()
p2 = mp.Process(target=run, args=(lock, _queue))
p2.start()
p2.join()