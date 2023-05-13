import os

import uasyncio
from models import events
from models.devices import Level2Device
from primitives.queue import Queue


class TinyS3Led:
    def __init__(self):
        import neopixel
        from machine import Pin
        from tinys3 import RGB_DATA, set_pixel_power
        self.led = neopixel.NeoPixel(Pin(RGB_DATA), 1)
        set_pixel_power(True)

    def get_color_from_wheel(self, color_index, brightness=0.5):
        from tinys3 import rgb_color_wheel
        r, g, b = rgb_color_wheel(color_index)
        return (r, g, b, brightness)

    def _apply(self, r, g, b, brightness):
        self.led[0] = (r, g, b, brightness)
        self.led.write()

    def red(self):
        self._apply(*self.get_color_from_wheel(0))

    def blue(self):
        self._apply(*self.get_color_from_wheel(100))

    def green(self):
        self._apply(*self.get_color_from_wheel(170))

    def orange(self):
        self._apply(*self.get_color_from_wheel(240))


async def led_coro(outgoing_led_queue: Queue, dev_to_process: list(Level2Device), debug_prints: bool = False):
    if os.uname()[4].startswith('TinyS3'):
        print("led_coro: TinyS3 detected")
        led = TinyS3Led()

        # Show startup LED for 6s
        led.blue()
        await uasyncio.sleep(6)

        while True:
            e = await outgoing_led_queue.get()

            # Analyze the Level 2 Devices last events and count
            count_rssi_ok_event = sum(1 for dev in dev_to_process if dev.get_last_event_type() == events.RssiOkEvent)
            count_rssi_low_event = sum(1 for dev in dev_to_process if dev.get_last_event_type() == events.RssiLowEvent)
            count_rssi_obs_event = sum(1 for dev in dev_to_process if dev.get_last_event_type() == events.RssiObsoleteEvent)

            if count_rssi_ok_event == len(dev_to_process):
                if debug_prints: print("led_coro: all 2nd level nodes RSSI values are OK")
                led.green()
            elif count_rssi_obs_event > 0:
                if debug_prints: print("led_coro: at least one 2nd level node RSSI value is obsolete")
                led.red()
            elif count_rssi_low_event > 0:
                if debug_prints: print("led_coro: at least one 2nd level node RSSI value is low")
                led.orange()

    else:
        print("led_coro: LED not implemented yet for this board")

    
