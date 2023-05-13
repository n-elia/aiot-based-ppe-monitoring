import os

import uasyncio


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
        
        
async def led_coro():
    if os.uname()[4].startswith('TinyS3'):
        led = TinyS3Led()

        while True:
            led.green()
            await uasyncio.sleep_ms(25)
            led.blue()
            await uasyncio.sleep_ms(25)
            led.green()
            await uasyncio.sleep_ms(25)
            led.blue()
            await uasyncio.sleep_ms(950)
            
    else:
        print("led_coro: LED not implemented yet for this board")
