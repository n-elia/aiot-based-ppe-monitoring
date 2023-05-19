"""Module that contains useful classes for managing the BLE."""

import time

import uasyncio
from models.devices import Level2Device

import aioble
from primitives.queue import Queue


class BLEManager:
    '''!
    Manages Bluetooth Low Energy.

    Manages BLE, and provides methods for continuously scan BLE devices 
    and update the 2nd level node objects.
    '''

    def __init__(
            self, cfg: dict = {}, 
            to_be_found: list(Level2Device) = None, 
            debug_prints=False, 
            logger_queue: Queue = None,
            preprocessor_queue: Queue = None
            ):
        self._debug_prints = debug_prints
        self._preprocessor_q = preprocessor_queue

        self._to_find = to_be_found
        self._to_find_names = [dev._name for dev in to_be_found]
        self._logger_queue = logger_queue
        if self._debug_prints:
            print("BLEManager: devices to be found: ", self._to_find_names)


    async def scan(self):
        async with aioble.scan(0, interval_us=30000, window_us=30000, active=True) as scanner:
            async for result in scanner:
                ts = time.time()
                ts_ticks_ms = time.ticks_ms()
                dev_name = result.name()
                dev_rssi = result.rssi

                if self._debug_prints:
                    print(
                        f"BLEManager: found device with name '{dev_name}', RSSI {dev_rssi}, at time {str(ts)}")

                if dev_name in self._to_find_names:
                    # Update the 2nd level node object
                    self._update_lvl_2_device(
                        name=dev_name, rssi=int(dev_rssi), ts=ts_ticks_ms)
                    # Send to logger queue
                    if self._logger_queue is not None:
                        await self._logger_queue.put(f"{time.time_ns()},{dev_name},{dev_rssi}")
                        await uasyncio.sleep(0)
                    await self._preprocessor_q.put(dev_name)
                    # TODO - Check if this is needed
                    await uasyncio.sleep(0)
        print("BLEManager: scan cycle terminated.")
        return

    def _update_lvl_2_device(self, name: str, rssi: int, ts: int):
        """!
        Update the 2nd level device.
        
        name: Name of the 2nd level device to update.
        rssi: RSSI value to save.
        ts: UNIX timestamp in which the RSSI measure has been taken.
        """
        if self._debug_prints:
            print(f"BLEManager: updating device with name '{name}'")
        for dev in self._to_find:
            if dev.get_name() == name:
                dev.update_rssi(rssi, ts)
