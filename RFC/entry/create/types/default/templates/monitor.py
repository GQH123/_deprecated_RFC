import time
import psutil


def net_usage(infs=['eth0', 'eth1']):
    if not isinstance(infs, list):
        infs = [infs]
    for inf in infs:
        print(f"current net-usage on interface {inf}:\n")
        net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inf]
        net_in_1 = net_stat.bytes_recv
        net_out_1 = net_stat.bytes_sent
        st_time = time.time()
        time.sleep(0.1)
        net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inf]
        net_in_2 = net_stat.bytes_recv
        net_out_2 = net_stat.bytes_sent
        ed_time = time.time()
        net_in = round((net_in_2 - net_in_1) / (ed_time-st_time) / 1024 / 1024, 3)
        net_out = round((net_out_2 - net_out_1) / (ed_time-st_time) / 1024 / 1024, 3)
        print(f"IN: {net_in} MB/s, OUT: {net_out} MB/s\n")


net_usage()