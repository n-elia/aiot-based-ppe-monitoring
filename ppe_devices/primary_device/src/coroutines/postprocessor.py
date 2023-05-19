from lib.primitives.queue import Queue
import lib.ocsvm as ocsvm
from models.events import RssiOkEvent, RssiNotOkEvent
import uasyncio

async def postprocessor_coro(
        processor_queue: Queue,
        outgoing_led_queue:Queue,
        outgoing_buzzer_queue:Queue,
        button: bool,
        debug_prints: bool
        ):
    
    print("postprocessor_coro: Inside postprocessor. Waiting for an event")
    last_event = -1

    while True:
        label = await processor_queue.get()
        
        if label != 1 and label != 0:
            print("postprocessor_coro: error in label")
            continue
        
       
        if label == 0:
            #print("label is 0")
            if last_event != 0:
                await outgoing_led_queue.put(label)
                await outgoing_buzzer_queue.put(label)
                last_event = label
                if debug_prints: print("postprocessor_coro: OK")
            else:
                if debug_prints:print("postprocessor_coro: Still OK")
                
        elif label == 1:
            #print("label is 1")

            if last_event != 1:
                #print("last_event is not 1 ")
                if debug_prints: print("postprocessor_coro: Alarm")
                await outgoing_led_queue.put(label)
                await outgoing_buzzer_queue.put(label)
                last_event = label
            else:
                
                if button:
                    await outgoing_buzzer_queue.put(0)
                    await outgoing_led_queue.put(0)
                    button = False
                if debug_prints: print("postprocessor_coro: Still Alarm")
        
        await uasyncio.sleep(0)

            
      
            