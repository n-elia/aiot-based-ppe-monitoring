"""Module that contains useful classes for managing the WiFi connection."""

import network
import ntptime

class WiFiManager:
    '''!
    Manage WiFi radio.

    Manage WiFi, and provide methods for connecting, disconnecting from an
    access point, and to update time.
    '''

    def __init__(self, ssid, password):
        """!
        Initializes a WiFiManager.
        
        ssid: SSID of the target WiFi network.
        password: Password of the target WiFi network.
        """
        self._wlan = network.WLAN(network.STA_IF)
        self._ssid = ssid
        self._password = password
 
    def do_connect(self):
        """Establish a connection to the target WiFi network."""
        self._wlan.active(True)

        if not self._wlan.isconnected():
            print('connecting to network...')
            self._wlan.connect(self._ssid, self._password)

            while not self._wlan.isconnected():
                pass
        
        print('network config:', self._wlan.ifconfig())

    def disconnect(self):
        """Closes the connection to the target WiFi network and shuts down the radio."""
        self._wlan.disconnect()
        self._wlan.active(False)

    def sync_RTC(self):
        """Synchronizes internal RTC by means of an NTP request."""
        import ntptime

        try:
            ntptime.settime()
        except:
            return False

        return True    