""" Test preprocessing speed.

This script tests the execution speed of the preprocessing algorithm.
"""

# Run also using the Unix port https://github.com/micropython/micropython/tree/master/ports/unix

from coroutines.preprocessor import Helmet, Shoes
from models.devices import Level2Device
import time
import random

def random_timestamp_ns(low_limit_ms, up_limit_ms):
    """Return a random timestamp in the range [low_limit_ms, up_limit_ms] in nanoseconds."""
    rnd = random.getrandbits(32)
    sign = 1
    if rnd % 2 == 0:
        sign = -1
    # Proportionate the random number to the range [low_limit_ms, up_limit_ms]
    rnd = rnd % (up_limit_ms - low_limit_ms)
    return (rnd + low_limit_ms) * 1000000

def random_timestamp_ms(low_limit_ms, up_limit_ms):
    """Return a random timestamp in the range [low_limit_ms, up_limit_ms] in milliseconds."""
    rnd = random.getrandbits(32)
    sign = 1
    if rnd % 2 == 0:
        sign = -1
    # Proportionate the random number to the range [low_limit_ms, up_limit_ms]
    rnd = rnd % (up_limit_ms - low_limit_ms)
    return (rnd + low_limit_ms)

# Create a set of mock Level2Device objects
mock_l2_device_h = Level2Device("mock_l2_device_h", "helmet")
mock_l2_device_rs = Level2Device("mock_l2_device_rs", "shoe_dx")
mock_l2_device_ls = Level2Device("mock_l2_device_ls", "shoe_sx")

# Create a mock Helmet object
mock_helmet = Helmet([mock_l2_device_h])

# Test the preprocessing of the mock Helmet object
n_rounds = 100
wcet_helmet = 0
for i in range(n_rounds):
    rssi = random.getrandbits(6) * (-1)
    ts = time.ticks_ms()
    mock_l2_device_h.update_rssi(
        rssi_value=rssi,
        timestamp=ts,
        )
    # Trigger the preprocessing of the mock Helmet object
    mock_helmet.trigger_preprocessing()

    # Wait for 100 +- 50 ms
    sleep_time = random_timestamp_ms(70, 150)
    time.sleep_ms(sleep_time)

    # Print the statistics of the mock Helmet object
    time_1 = time.time_ns()
    count, avg_rssi, avg_variance, avg_std_dev = mock_helmet.get_statistics()
    time_2 = time.time_ns()
    ex_time_ms = (time_2-time_1)/1000000
    if ex_time_ms > wcet_helmet:
        wcet_helmet = ex_time_ms
    print(f"Mock Helmet: count = {count}, avg_rssi = {avg_rssi}, avg_variance = {avg_variance}, avg_std_dev = {avg_std_dev}")
    print(f"Mock Helmet: Elapsed time for computation: {(time_2-time_1)/1000000}ms \n")

print(f"Helmet - WCET = {wcet_helmet}ms \n")
time.sleep(5)

# Create a mock Shoes object
mock_shoes = Shoes([mock_l2_device_rs, mock_l2_device_ls])

# Test the preprocessing of the mock Shoes object
wcet_shoes = 0
for i in range(200):
    rssi_rs = random.getrandbits(6) * (-1)
    rssi_ls = random.getrandbits(6) * (-1)
    ts = time.ticks_ms()
    mock_l2_device_rs.update_rssi(
        rssi_value=rssi_rs,
        timestamp=ts,
        )
    mock_l2_device_ls.update_rssi(
        rssi_value=rssi_ls,
        timestamp=ts,
        )
    # Trigger the preprocessing of the mock Shoes object
    mock_shoes.trigger_preprocessing()

    # Wait for 100 +- 50 ms
    sleep_time = random_timestamp_ms(50, 150)
    time.sleep_ms(sleep_time)

    # Print the statistics of the mock Shoes object
    time_1 = time.time_ns()
    count, avg_rssi, avg_variance, avg_std_dev = mock_shoes.get_statistics()
    time_2 = time.time_ns()
    ex_time_ms = (time_2-time_1)/1000000
    if ex_time_ms > wcet_shoes:
        wcet_shoes = ex_time_ms
    print(f"Mock Shoes: count = {count}, avg_rssi = {avg_rssi}, avg_variance = {avg_variance}, avg_std_dev = {avg_std_dev}")
    print(f"Mock Shoes: Elapsed time for computation: {ex_time_ms}ms \n")

print(f"Shoes - WCET = {wcet_shoes}ms \n")
