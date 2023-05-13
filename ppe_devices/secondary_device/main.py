import json
import time
import sys

import aioble
import uasyncio
from led import led_coro
from micropython import const

MS_TO_US = 1000

# Configuration file
_CFG_FILENAME = "config.json"


async def main_loop(cfg_dict: dict):
    h = []

    # BLE task
    h.append(uasyncio.create_task(ble_coro(
        device_ble_name=cfg_dict["device_ble_name"],
        adv_interval_ms=cfg_dict["adv_interval_ms"]
    )))
    
    # LED task
    h.append(uasyncio.create_task(led_coro()))

    while True:
        try:
            print('main_loop: running...')
            await uasyncio.sleep(10)
        except KeyboardInterrupt:
            for h_i in h:
                h_i.cancel()
            print('main_loop: interrupted')
            return


async def ble_coro(device_ble_name: str, adv_interval_ms: int):
    reset_interval_s = 20
    
    while True:
        print("ble_coro: starting BLE GAP coroutine...")
        h = uasyncio.create_task(ble_adv_coro(
            device_ble_name=device_ble_name,
            adv_interval_ms=adv_interval_ms
        ))

        print(f"ble_coro: waiting for {reset_interval_s}s...")
        await uasyncio.sleep(reset_interval_s)

        print("ble_coro: cancelling BLE GAP coroutine...")
        h.cancel()

        await uasyncio.sleep_ms(5)


async def ble_adv_coro(device_ble_name: str, adv_interval_ms: int):
    while True:
        print("ble_adv_coro: starting BLE GAP advertising...")
        # Start GAP advertising
        await aioble.advertise(
            adv_interval_ms * MS_TO_US,
            name=device_ble_name,
            services=[],
            appearance=const(512),  # generic tag
            connectable=False
        )


if __name__ == '__main__':
    # Load configuration file
    cfg = {}

    try:
        with open(_CFG_FILENAME, 'r') as cfg_fp:
            cfg = json.load(cfg_fp)
            print("main: loaded config:\n", cfg)
    except:
        print("main: error while reading config file")
        sys.exit()

    # Run the main task
    try:
        uasyncio.run(main_loop(cfg_dict=cfg))
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        uasyncio.new_event_loop()  # Clear retained state

