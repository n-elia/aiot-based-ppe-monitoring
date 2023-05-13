""" Test processing speed.

This script tests the execution speed of the SVM inference function.
"""
from utime import ticks_diff, ticks_us
from svm import score


def timed_function(f, *args, **kwargs):
    myname = str(f).split(' ')[1]
    def new_func(*args, **kwargs):
        t = ticks_us()
        result = f(*args, **kwargs)
        delta = ticks_diff(ticks_us(), t)
        print('Function: {}. Execution time = {:6.3f}ms'.format(myname, delta/1000))
        return result
    return new_func


@timed_function
def inference_timed():
    input_array = [28, -61.04, 0.93, 0.96, 14, -73.88, 0.53, 0.73]
    return score(input_array)

def inference():
    input_array = [28, -61.04, 0.93, 0.96, 14, -73.88, 0.53, 0.73]
    return score(input_array)


def main():
    result = inference_timed()
    print(f"Result: {result}")
    
    n_runs = 1000
    print(f"Averaging execution time over {n_runs} runs...")
    total_time = 0
    for i in range(n_runs):
        t = ticks_us()
        result = inference()
        delta = ticks_diff(ticks_us(), t)
        total_time += delta
    
    print(f"Average execution time: {total_time/1000/n_runs}ms")

if __name__ == '__main__':
    main()
