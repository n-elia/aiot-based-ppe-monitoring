import utime
from machine import Pin

def button_pressed_handler(button):
    button = True
    return button

async def button_coro(button: bool,  debug_prints: bool = False):
    button_pin = Pin(13, Pin.IN, Pin.PULL_DOWN)  #23 number pin is input

    button_pin.irq(trigger=Pin.IRQ_FALLING, handler = button_pressed_handler(button))
