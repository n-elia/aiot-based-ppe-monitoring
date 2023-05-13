"""Submodule that stores devices definitions."""

import time
from models import events
from lib.rssi_circular_buffer import WindowedCircularBuffer

class DeviceType:
    """Enum class that defines the type of a device."""
    HELMET = "helmet"
    SHOE_DX = "shoe_dx"
    SHOE_SX = "shoe_sx"

class Level2Device:
    def __init__(self, name: str, dev_type: str, buf_len = 50, buf_window_s = 5):
        self._name = name
        self._type = dev_type
        self._last_event = None
        self._buffer = WindowedCircularBuffer(buf_len, buf_window_s)

    def update_rssi(self, rssi_value: int, timestamp: int):
        self._buffer.append(rssi_value, timestamp)
    
    def get_name(self) -> str:
        """Returns the device name."""
        return self._name
    
    def get_type(self) -> str:
        """Returns the device type."""
        return self._type

    def get_rssi(self):
        return self._buffer.get_window_avg()

    def get_count(self):
        return self._buffer.get_window_count()
    
    def get_buffer_len(self):
        return len(self._buffer)

    def update_last_event(self, event: events.RssiEvent):
        self._last_event = event

    def get_last_event_type(self):
        return type(self._last_event)

def check_device_types(devices_list: list[Level2Device]) -> bool:
    """Check if the device types are valid.
    In this case, valid means that the devices are 3 and each one of them is of a different DeviceType.
    Returns True if the device types are valid, False otherwise.
    
    devices_list: List of devices to check.
    """
    if len(devices_list) != 3:
        print("check_device_types: Invalid number of devices: %d", len(devices_list))
        return False

    dev_types = [dev.get_type() for dev in devices_list]

    if (
        DeviceType.HELMET not in dev_types or
        DeviceType.SHOE_DX not in dev_types or
        DeviceType.SHOE_SX not in dev_types
    ):
        print("check_device_types: Invalid device types: %s", dev_types)
        return False
    else:
        return True
