import multiprocessing as mp


MANAGER = mp.Manager()
MANAGER_LOCK = MANAGER.RLock()