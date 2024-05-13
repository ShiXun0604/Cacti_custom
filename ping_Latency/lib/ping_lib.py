import os
from queue import Queue
from threading import Lock


# Variant
global ping_queue, lock 
ping_queue = {}
lock = {}

def ping_and_save(host, interval):
    global ping_queue, lock
    response = os.popen(f'ping -n 1  {host}').read()
    try:
        # data = response.split('\n')[2].split(' ')[3][3:].strip('ms')  # 中文cmd
        data = response.split('\n')[2].split(' ')[4][5:].strip('ms')  # 英文cmd
    except:
        data = None
   
    # keep queue length = interval
    lock[host].acquire()
    ping_queue[host].put(data)
    if ping_queue[host].qsize() > interval:
        ping_queue[host].get() 
    lock[host].release()





