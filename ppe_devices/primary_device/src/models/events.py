"""Submodule that stores events definitions."""
import json


class BatteryEvent:
    def __init__(self, voltage, timestamp) -> None:
        self._voltage = voltage
        self._timestamp = timestamp

    def get_voltage(self):
        return self._type

    def get_measure_timestamp(self):
        return self._timestamp


class RssiEvent:
    """!
    Generic RSSI event.
    
    This serves as base class for RSSI-related events.
    """
    _type = "event_type"

    def __init__(self, dev_name, rssi, timestamp) -> None:
        """!
        Initialize an RSSI event regarding a specific device.
        
        dev_name: Name of the involved device.
        rssi: Measured RSSI.
        timestamp: UNIX timestamp in which the RSSI measure has been taken.
        """
        self._dev_name = dev_name
        self._rssi = rssi
        self._timestamp = timestamp

    def backend_msg(self):
        """Convert the event into a message for backend server."""
        json_msg = {
            "event_type": self._type,
            "dev_name": self._dev_name,
            "dev_rrsi": self._rssi,
            "dev_t": self._timestamp
        }
        return json.dumps(json_msg)

    def get_device_name(self):
        """Return the device name."""
        return self._dev_name

    def get_type(self):
        """Return the RSSI Event type."""
        return self._type

    def get_device_rssi(self):
        return self._rssi

    def get_device_timestamp(self):
        return self._timestamp


class RssiLowEvent(RssiEvent):
    """RSSI event that occurs whenever the RSSI is too low. """

    _type = "RSSI_LOW"

    def __init__(self, dev_name, rssi, timestamp) -> None:
        super().__init__(dev_name, rssi, timestamp)


class RssiObsoleteEvent(RssiEvent):
    """RSSI event that occurs whenever the latest RSSI measurement is too old. """

    _type = "RSSI_OBSOLETE"

    def __init__(self, dev_name, rssi, timestamp) -> None:
        super().__init__(dev_name, rssi, timestamp)


class RssiOkEvent(RssiEvent):
    """RSSI event that occurs whenever the RSSI is OK."""

    _type = "RSSI_OK"

    def __init__(self, dev_name, rssi, timestamp) -> None:
        super().__init__(dev_name, rssi, timestamp)


class RssiNullEvent(RssiEvent):
    _type = "RSSI_NULL"

    def __init__(self, dev_name, rssi, timestamp) -> None:
        super().__init__(dev_name, rssi, timestamp)
        
class RssiNotOkEvent(RssiEvent):
    _type = "RSSI_NOT_OK"

    def __init__(self, dev_name, rssi, timestamp) -> None:
        super().__init__(dev_name, rssi, timestamp)