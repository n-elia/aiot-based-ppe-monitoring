""" Test buffer speed.

This script tests the execution speed of different buffer implementations.
"""

from array import array

class CircularBuffer(object):
    ''' Very simple implementation of a circular buffer based on lists '''
    def __init__(self, max_size):
        self.max_size = max_size
        self._init()

    def _init(self):
        self.data = [0] * self.max_size
        self._i = 0
        self._wrapped = False

    def __len__(self):
        if self._wrapped:
            return self.max_size
        else:
            return self._i

    def is_empty(self):
        return len(self) == 0

    def append(self, item):
        self.data[self._i] = item
        self._i = (self._i + 1) % self.max_size
        if self._i == 0:
            self._wrapped = True

    def read(self):
        if self._wrapped:
            return self.data[self._i:] + self.data[:self._i]
        else:
            return self.data[:self._i]
    
    def reverse_read(self):
        if self._wrapped:
            return self.data[:self._i][::-1] + self.data[self._i:][::-1]
        else:
            return self.data[:self._i][::-1]

class CircularBufferArray(object):
    ''' Very simple implementation of a circular buffer based on array '''
    def __init__(self, max_size):
        self.max_size = max_size
        self._init()

    def _init(self):
        self.data = array('f', [0]*self.max_size)
        self._i = 0
        self._wrapped = False

    def __len__(self):
        if self._wrapped:
            return self.max_size
        else:
            return self._i

    def is_empty(self):
        return len(self) == 0

    def append(self, item):
        self.data[self._i] = item
        self._i = (self._i + 1) % self.max_size
        if self._i == 0:
            self._wrapped = True

    def read(self):
        if self._wrapped:
            return self.data[self._i:] + self.data[:self._i]
        else:
            return self.data[:self._i]
        
import time
import random

def compute_avg(input_list):
    if len(input_list) == 0:
        print("compute_avg: the input list is empty")
        return None
    return sum(input_list) / len(input_list)

max_size=50*5

rssi_buff = CircularBuffer(max_size=max_size)
ts_buff = CircularBuffer(max_size=max_size)

# Fill the CircularBuffers
for i in range(max_size):
    rssi_buff.append(random.getrandbits(6) * (-1))
    ts_buff.append(time.time_ns())

time_0 = time.time_ns()
window_size = 50
i_low = 0
i_high = window_size
rssi_buff_read = rssi_buff.read()
# Compute the average of all the found windows
n = len(rssi_buff_read)
for i in range(n-window_size):
    print(i_low)
    curr_window = rssi_buff_read[i_low:i_high]
    print(f"window average: {compute_avg(curr_window)}")
    i_low += 1
    i_high += 1
    
    if i_high > n:
        break
time_1 = time.time_ns()
print(f"total time: {(time_1-time_0)/1000000}ms")

# Do the same with array-based implementation

rssi_buff = CircularBufferArray(max_size=max_size)
ts_buff = CircularBufferArray(max_size=max_size)

# Fill the CircularBuffers
for i in range(max_size):
    rssi_buff.append(random.getrandbits(6) * (-1))
    ts_buff.append(time.time_ns())

time_0 = time.time_ns()
window_size = 50
i_low = 0
i_high = window_size
rssi_buff_read = rssi_buff.read()
# Compute the average of all the found windows
n = len(rssi_buff_read)
for i in range(n-window_size):
    print(i_low)
    curr_window = rssi_buff_read[i_low:i_high]
    print(f"window average: {compute_avg(curr_window)}")
    i_low += 1
    i_high += 1
    
    if i_high > n:
        break
time_1 = time.time_ns()
print(f"total time: {(time_1-time_0)/1000000}ms")

