import gc
import json
import sys

import uasyncio
from machine import PWM, Pin, SoftI2C
from primitives.queue import Queue
from wifi_manager import WiFiManager

from coroutines.ble import ble_coro
from coroutines.peripherals.led import led_coro
from coroutines.logger import file_logger_coro
from models.devices import Level2Device, check_device_types

# Configuration file
_CFG_FILENAME = "config.json"


async def main_loop(cfg_dict: dict, i2c_instance: SoftI2C):
    '''
    This coroutine will start the necessary tasks, saving their handles in coro_handles list.

    cfg_dict: Configuration dictionary.
    i2c_instance: I2C bus instance.
    '''
    coro_handles = []

    # Create a Queue for events led
    led_q = Queue(maxsize=10)
    # Create a Queue for logger events
    logger_q = Queue(maxsize=20)
    # Create a Queue for the preprocessor coroutine
    preprocessor_q = Queue(maxsize=10)

    # Create 2nd level device objects
    level_2_devices = []
    for dev_name, dev_type in zip(cfg_dict["to_find_names"], cfg_dict["to_find_types"]):
        level_2_devices.append(Level2Device(name=dev_name, dev_type=dev_type))
    if not check_device_types(level_2_devices):
        print("main_loop: Error: device types are not valid.")
        sys.exit()

    # Create Buzzer task
    # buzzer_coro_handle = uasyncio.create_task(buzzer_coro(
    #     outgoing_buzzer_queue=buzzer_q,
    #     dev_to_process=level_2_devices
    # ))
    # coro_handles.append(buzzer_coro_handle)

    # Create Led output processor task
    led_coro_handle = uasyncio.create_task(led_coro(
        outgoing_led_queue=led_q,
        dev_to_process=level_2_devices
    ))
    coro_handles.append(led_coro_handle)

    # Create BLE scan task
    ble_coro_handle = uasyncio.create_task(ble_coro(
        to_be_found=level_2_devices,
        debug_prints=cfg_dict["ble_enable_debug_print"],
        enable_logging=cfg_dict["logger_enable"] or False,
        logger_queue=logger_q,
        preprocessor_queue=preprocessor_q
    ))
    coro_handles.append(ble_coro_handle)

    # Create backend communication task
    # backend_communication_coro_handle = uasyncio.create_task(backend_communication_coro(
    #     hostname=cfg_dict["backend_hostname"],
    #     port=cfg_dict["backend_port"],
    #     outgoing_messages_queue=outgoing_q,
    #     enabled=cfg_dict["backend_comm_enable"]
    # ))
    # coro_handles.append(backend_communication_coro_handle)

    # Create file logger task
    if cfg_dict["logger_enable"]:
        file_logger_coro_handle = uasyncio.create_task(file_logger_coro(
            logger_queue=logger_q,
            debug_prints=cfg_dict["logger_enable_debug_print"],
        ))
        coro_handles.append(file_logger_coro_handle)

    try:
        while True:
            # Run garbage collection
            if cfg_dict["main_enable_debug_print"]: print(f"main_loop: allocated heap: {gc.mem_alloc()}")
            if cfg_dict["main_enable_debug_print"]: print(f"main_loop: running garbage collection...")
            gc.collect()
            if cfg_dict["main_enable_debug_print"]: print(f"main_loop: allocated heap: {gc.mem_alloc()}")
            
            # Sleep for 10 seconds
            if cfg_dict["main_enable_debug_print"]: print(f"main_loop: sleeping for 10 seconds...")
            await uasyncio.sleep(10)
    except KeyboardInterrupt:
        print("main_loop: KeyboardInterrupt: exiting...")
        for coro_handle in coro_handles:
            coro_handle.cancel()
        sys.exit(0)

if __name__ == "__main__":
    # Enable garbage collector
    gc.enable()

    # Load configuration file
    cfg = {}

    try:
        with open(_CFG_FILENAME, 'r') as cfg_fp:
            cfg = json.load(cfg_fp)
            print("main: loaded config:\n", cfg)
    except:
        print("main: error while reading config file")
        sys.exit()

    # Initialize I2C bus
    i2c = SoftI2C(sda=Pin(8),  # Here, use your I2C SDA pin
                  scl=Pin(9),  # Here, use your I2C SCL pin
                  freq=400000)  # Fast: 400kHz, slow: 100kHz

    # Establish WiFi connection and RTC sync
    wm = WiFiManager(cfg["wifi_ssid"], cfg["wifi_pass"])
    if "backend_comm_enable" not in cfg or cfg["backend_comm_enable"] == True:
        wm.do_connect()
        wm.sync_RTC()

    # Run the control task
    try:
        uasyncio.run(main_loop(cfg_dict=cfg, i2c_instance=i2c))
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        uasyncio.new_event_loop()  # Clear retained state
