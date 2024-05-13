from queue import Queue
import os
from threading import Lock


# 執行此段必須將資源上鎖
def calculate_average(queue):
    if queue.qsize() == 0:
        return None
    
    total_sum = 0
    count = 0
    err = 0
    temp_queue = Queue()

    while not queue.empty():
        item = queue.get()
        if item != None:
            total_sum += int(item)
            count += 1
        else:
            err += 1
        temp_queue.put(item)
   
    while not temp_queue.empty():
        queue.put(temp_queue.get())

    if count == 0:
        return ['NULL', 'NULL']

    average = total_sum / count

    return [average, err]


# 執行此段必須將資源上鎖
def return_queue_contents(queue):
    temp_queue = Queue()

    result_info = ''
    while not queue.empty():
        item = queue.get()
        result_info += '{}  '.format(item)
        temp_queue.put(item)
    while not temp_queue.empty():
        item = temp_queue.get()
        queue.put(item)
    
    return result_info
