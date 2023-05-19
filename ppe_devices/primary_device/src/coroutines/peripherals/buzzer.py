import time

from machine import PWM, Pin
from models import events
from models.devices import Level2Device
from primitives.queue import Queue


async def buzzer_coro(outgoing_buzzer_queue: Queue, dev_to_process: list(Level2Device), debug_prints: bool = False):
    #print("buzzer_coro: Dentro buzzer_coro")

    PIN_NUMBER = 5
    PWM_FREQUENCY = 1047
    PWM_DUTY_CYCLE = 512  # range 0-1023 (0% - 100%)
    buzzer_pin = Pin(PIN_NUMBER, Pin.OUT)

    buzzer = PWM(buzzer_pin)     # create PWM object from a pin
    buzzer.freq(PWM_FREQUENCY)   # set PWM frequency from 1Hz to 40MHz
    # duty cycle, range 0-1023 (default 512, 50%)
    buzzer.duty(PWM_DUTY_CYCLE)

    time.sleep_ms(1000)

    buzzer.duty(0)
    #buzzer.deinit()

    while True:
        e = await outgoing_buzzer_queue.get()

        if e == 1:
            if debug_prints: print("buzzer_coro: *** Suono del buzzer ***")
            buzzer.duty(PWM_DUTY_CYCLE)
        elif e  == 0:
            if debug_prints: print("buzzer_coro: *** Stop suono del buzzer ***")
            buzzer.duty(0)
