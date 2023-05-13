import time

from machine import PWM, Pin
from models import events
from models.devices import Level2Device
from primitives.queue import Queue


async def buzzer_coro(outgoing_buzzer_queue: Queue, dev_to_process: list(Level2Device)):
    print("buzzer_coro: Dentro buzzer_coro")

    if 1 == 2:  # [TODO] Eliminare per attivare il buzzer
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
        buzzer.deinit()

    while True:
        e = await outgoing_buzzer_queue.get()
        e_type = type(e)

        if e_type == events.RssiLowEvent:
            print("buzzer_coro: *** Suono del buzzer ***")
            # SUONO DEL BUZZER

        elif e_type == events.RssiObsoleteEvent:
            print("buzzer_coro: *** Suono del buzzer ***")
            # SUONO DEL BUZZER
