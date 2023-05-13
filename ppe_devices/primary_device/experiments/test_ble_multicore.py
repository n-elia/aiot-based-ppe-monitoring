""" Test BLE multicore

This script tests the BLE multicore functionality of the ESP32.
The BLE functionality is run on the second core, while the main
loop (i.e., the MicroPython firmware) is run on the first core.

The BLE functionality is implemented using the `aioble` library.
The main loop is implemented using the `uasyncio` library.

Example of output with 3 BLE devices in range, broadcasting at
a rate of 10Hz each:
---
blocking_coro: Tick 1 - async sleep 80ms
read_coro: read message 812.3234,test-device,-71 from queue
blocking_coro: Tick 2 - blocking sleep 20ms
blocking_coro: Tick 1 - async sleep 80ms
read_coro: read message 812.4548,test-device,-70 from queue
read_coro: read message 812.4571,test-device,-66 from queue
blocking_coro: Tick 2 - blocking sleep 20ms
blocking_coro: Tick 1 - async sleep 80ms
read_coro: read message 812.5709,test-device,-71 from queue
read_coro: read message 812.5945,test-device,-71 from queue
blocking_coro: Tick 2 - blocking sleep 20ms
blocking_coro: Tick 1 - async sleep 80ms
read_coro: read message 812.7036,test-device,-69 from queue
read_coro: read message 812.7334,test-device,-68 from queue
blocking_coro: Tick 2 - blocking sleep 20ms
blocking_coro: Tick 1 - async sleep 80ms
read_coro: read message 812.8416,test-device,-64 from queue
read_coro: read message 812.8433,test-device,-65 from queue
blocking_coro: Tick 2 - blocking sleep 20ms
blocking_coro: Tick 1 - async sleep 80ms
read_coro: read message 812.8622,test-device,-70 from queue
blocking_coro: Tick 2 - blocking sleep 20ms
blocking_coro: Tick 1 - async sleep 80ms
read_coro: read message 812.9937,test-device,-68 from queue
read_coro: read message 812.9955,test-device,-71 from queue
read_coro: read message 813.0139,test-device,-69 from queue
blocking_coro: Tick 2 - blocking sleep 20ms
blocking_coro: Tick 1 - async sleep 80ms
read_coro: read message 813.1117,test-device,-65 from queue
read_coro: read message 813.1229,test-device,-65 from queue
read_coro: read message 813.1433,test-device,-71 from queue
blocking_coro: Tick 2 - blocking sleep 20ms
blocking_coro: Tick 1 - async sleep 80ms
read_coro: read message 813.2422,test-device,-70 from queue
read_coro: read message 813.2634,test-device,-70 from queue
read_coro: read message 813.2699,test-device,-67 from queue
blocking_coro: Tick 2 - blocking sleep 20ms
---

This demonstrates that the BLE functionality is running in the
background, while the main loop is running on the first core.
The BLE functionality is able to find all 3 devices, and the
main loop is able to read the messages from the BLE scanner
queue.
One possible issue is that `aioble` library does not store the
time stamp of when the message was received from the BLE scanner.
Instead, the time stamp is added to the message when it is read
from the queue. This means that the time stamp is the time at
which the message was read from the queue, not the time at which
the message was received from the BLE scanner.

"""

import gc
import sys
import time

import aioble
import uasyncio
from ble_manager import BLEManager
from coroutines.ble import ble_coro
from primitives.queue import Queue


NS_TO_MS = 1e-6
NS_TO_S = 1e-9

class BLEManager:
    def __init__(self, to_be_found, out_queue: Queue = None):
        self._to_find_names = to_be_found
        self._out_queue = out_queue

    async def scan(self):
        # Note: `scanner` seems to be an async generator that yields
        #       `aioble.ScanResult` objects. The `async for` loop
        #       seems to be the only way to get the results.
        #       The `scanner` is populated with results as they are
        #       found. This happens in the background, because the
        #       BLE functionality is running on a separate core.
        async with aioble.scan(
            0, interval_us=30000, window_us=30000, active=True
        ) as scanner:
            async for result in scanner:
                dev_name = result.name()
                # print(f"found device with name {dev_name}")
                dev_rssi = result.rssi

                if dev_name in self._to_find_names:
                    # Note: `time.time_ns()` returns the current time in
                    #       nanoseconds. This is converted to seconds
                    #       and appended to the message.
                    #       This is done each time a message is read from
                    #       the BLE scanner queue. This means that the time
                    #       stamp is the time at which the message was read
                    #       from the queue, not the time at which the message
                    #       was received from the BLE scanner.
                    #       One possible solution is to add the time stamp
                    #       to the `aioble.ScanResult` object, but this
                    #       would require modifying the `aioble` library.
                    # https://github.com/micropython/micropython-lib/blob/a1b9aa934c306a45849faa19d12cffe6bfd89d4c/micropython/bluetooth/aioble/aioble/central.py#L141
                    await self._out_queue.put(f"{time.time_ns()*NS_TO_S},{dev_name},{dev_rssi}")
                    await uasyncio.sleep(0)
        return


async def ble_coro(to_be_found, out_queue: Queue):
    ble_device = BLEManager(
        to_be_found=to_be_found,
        out_queue=out_queue,
    )
    await ble_device.scan()


async def read_coro(in_queue: Queue):
    while True:
        while not in_queue.empty():
            msg = await in_queue.get()
            print(f"read_coro: read message {msg} from queue")
            
        await uasyncio.sleep_ms(3)

async def blocking_coro():
    # Supposing that we divide our time into 100ms blocks, we can
    # sleep for 20ms in the async coro and 80ms in the blocking coro.
    # If we will receive all the messages from the BLE scanner queue
    # in the async coro, then we will have 80ms to process them in
    # the blocking coro.
    _async_sleep_ms = 20
    _blocking_sleep_ms = 80

    while True:
        print(f"blocking_coro: Tick 1 - async sleep {_async_sleep_ms}ms")
        await uasyncio.sleep_ms(_async_sleep_ms)
        print(f"blocking_coro: Tick 2 - blocking sleep {_blocking_sleep_ms}ms")
        time.sleep_ms(_blocking_sleep_ms)

async def main_loop():
    coro_handles = []

    # Create a Queue for BLE scan outputs
    ble_queue = Queue(maxsize=10)

    # Create 2nd level device objects
    level_2_devices = []
    level_2_devices.append("test-device")

    # Create BLE scan task
    ble_coro_handle = uasyncio.create_task(
        ble_coro(
            to_be_found=level_2_devices,
            out_queue=ble_queue,
        )
    )
    coro_handles.append(ble_coro_handle)

    # Create read coro task
    read_coro_handle = uasyncio.create_task(
        read_coro(
            in_queue=ble_queue,
        )
    )
    coro_handles.append(read_coro_handle)

    # Create blocking coro task
    blocking_coro_handle = uasyncio.create_task(
        blocking_coro()
    )
    coro_handles.append(blocking_coro_handle)

    try:
        while True:
            # Run garbage collection
            gc.collect()

            # Sleep for 10 seconds
            await uasyncio.sleep(10)
    except KeyboardInterrupt:
        print("main_loop: KeyboardInterrupt: exiting...")
        for coro_handle in coro_handles:
            coro_handle.cancel()
        sys.exit(0)


if __name__ == "__main__":
    # Enable garbage collector
    gc.enable()

    # Run the main loop task
    try:
        uasyncio.run(main_loop())
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        uasyncio.new_event_loop()  # Clear retained state
