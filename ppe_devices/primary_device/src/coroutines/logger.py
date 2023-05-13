import gc
import os
import time

import uasyncio
from primitives.queue import Queue

SAVE_INTERVAL_S = 10

async def file_logger_coro(logger_queue: Queue, debug_prints: bool = False):
    base_filename = "log.csv"
    filename_head = base_filename.split(".")[0]
    filename_tail = base_filename.split(".")[1]

    files = os.listdir()
    i = 1
    for f in files:
        if f.startswith(filename_head):
            i += 1
    filename_no = "_" + str(i)

    filename = filename_head + filename_no + "." + filename_tail

    print(f"file_logger_coro: creating file '{filename}'...")
    with open(filename, 'w') as f:
        f.write("timestamp_ns,device_name,rssi\n")
        if debug_prints: print(f"file_logger_coro: wrote header to '{filename}'")

    try:
        f = open(filename, 'a')
        if debug_prints: print(f"file_logger_coro: opened file '{filename}' for appending")
        log_start_time = time.time()

        while True:
            line = await logger_queue.get()

            b = f.write(line + "\n")

            if debug_prints: print(f"file_logger_coro: wrote '{b}' bytes, line '{line}'")
            
            if log_start_time + SAVE_INTERVAL_S < time.time():
                if debug_prints: print(f"file_logger_coro: flushing file '{filename}'...")
                f.flush()
                log_start_time = time.time()
            
    except uasyncio.CancelledError:
        print("file_logger_coro: CancelledError: exiting...")
        f.close()
    except:
        print("file_logger_coro: unknown error. Exiting...")
        f.close()
