""" Test postprocessing speed.

This script tests the execution speed of a sample postprocessing algorithm.
"""

import time

class PostProcessingAlgorithm():
    def __init__(self, threshold = 10):
        self.warn_count = 0
        self.threshold = threshold
        
    def add_processing_result(self, result):
        if result < 0:
            self.warn_count += 1
        else:
            self.warn_count = 0
    
    def evaluate_alarm_state(self):
        if self.warn_count >= self.threshold:
            return True
        else:
            return False
        
example_result_series = [ 1, -1, 1, -1, -1, -1, -1, -1, 1, -1, -1, -1, -1, -1, -1, 1,
                         -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 1, -1 ]

def main():
    pp = PostProcessingAlgorithm()
    
    wcet = 0    
    for r in example_result_series:
        time_1 = time.time_ns()
        
        pp.add_processing_result(r)
        ev = pp.evaluate_alarm_state()
        if ev is True:
            print("Alarm active")
        
        time_2 = time.time_ns()
        ex_time_ms = (time_2-time_1)/1000000
        if ex_time_ms > wcet:
            wcet = ex_time_ms
    
    print("Expected number of alarms: 3")
    print(f"WCET = {wcet}ms")
    
if __name__ == '__main__':
    main()
