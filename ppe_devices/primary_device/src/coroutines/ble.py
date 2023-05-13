from ble_manager import BLEManager
from models.devices import Level2Device
from primitives.queue import Queue
from uasyncio import Event


async def ble_coro(to_be_found: list(Level2Device), debug_prints: bool, enable_logging: bool, logger_queue: Queue, preprocessor_queue: Queue):
    ble_device = BLEManager(
        to_be_found=to_be_found,
        debug_prints=debug_prints,
        logger_queue=logger_queue if enable_logging else None,
        preprocessor_queue=preprocessor_queue
        )
    await ble_device.scan()
