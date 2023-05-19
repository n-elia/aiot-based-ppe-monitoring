import time
import math
from collections import deque

class CircularBuffer(object):
    ''' Very simple implementation of a circular buffer based on lists '''
    def __init__(self, max_size):
        self.max_size = max_size
        self._init()

    def _init(self):
        # self.data = [0] * self.max_size
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
        
        # return self.read()[::-1]

class WindowedCircularBuffer(object):
    def __init__(self, max_size, time_window_s):
        self.max_size = max_size
        self.time_window = time_window_s * 1000 # to ms
        self.values = CircularBuffer(max_size)
        self.timestamps = CircularBuffer(max_size)

    def __len__(self):
        return len(self.values)

    def is_empty(self):
        return self.values.is_empty()

    def append(self, rssi, time_ms):
        self.values.append(rssi)
        self.timestamps.append(time_ms)

    def get_window(self):
        """Return 2 lists: rssi, timestamp belonging to the last time window."""
        now = time.ticks_ms()
        
        timestamp_values = self.timestamps.reverse_read()
        ret_ts = []
        j = 0

        for i in range(len(timestamp_values)):
            if time.ticks_diff(now, timestamp_values[i]) <= self.time_window:
                ret_ts.append(timestamp_values[i])
                j += 1
            else:
                break

        return self.values.reverse_read()[:j], ret_ts
    
    def get_window_count(self):
        """Returns the number of values in the last time window."""
        now = time.ticks_ms()
        i = 0

        for ts in self.timestamps.read():
            if self.time_window <= time.ticks_diff(now, ts):
                i += 1
            else:
                break
        return i
    
    def get_window_values(self):
        """Returns a list of the values in the last time window."""
        return self.get_window()[0]
    
    def get_window_avg(self):
        """Returns the average of the values in the last time window."""
        window_values = self.get_window_values()

        window_values_len = len(window_values)

        if window_values_len == 0:
            return None, 0

        s = 0
        for x in window_values:
            s += x
        return s / window_values_len, window_values_len
    
    def get_window_variance(self, ddof=0):
        """Returns the variance of the values in the last time window.
           Returns a tuple (variance, count)."""
        data = self.get_window_values()
        n = len(data)
        if n == 0:
            return None, 0
        mean = sum(data) / n
        # return sum((x - mean) ** 2 for x in data) / (n - ddof), n
        return sum(math.pow((x - mean), 2) for x in data) / (n - ddof), n
    
    def get_window_std_dev(self):
        """Returns the standard deviation of the values in the last time window.
        Returns a tuple (std_dev, count)."""
        var, n = self.get_window_variance()
        return math.sqrt(var), n
    
    def get_window_var_std_dev(self):
        """Returns the variance and standard deviation of the values in the last time window.
        Returns a tuple (variance, std_dev, count)."""
        var, n = self.get_window_variance()
        if var is None:
            return None, None, 0
        return var, math.sqrt(var), n

def is_list_sorted(l):
    return all(l[i] <= l[i+1] for i in range(len(l)-1))