from lib.primitives.queue import Queue
import uasyncio
import lib.ocsvm as ocsvm
from coroutines.preprocessor import Shoes, Helmet


async def processor_coro(
        processor_queue: Queue,
        debug_prints: bool,
        processables: list
        ):
    print("processor_coro: Inside processor coro. Waiting for an input")
    h = []
    s = []
    while True:

        if processables != []:
            for p in processables:

                if isinstance(p, Helmet) :
                    h = p.get_statistics()
                elif isinstance(p, Shoes):
                    s = p.get_statistics()
                else:
                    print("processor_coro: Object is not an Helmet or a Shoe")
                    
            input_array = []
            input_array.extend(h)
            input_array.extend(s)
            print(input_array)
            if input_array != []:
                pred = ocsvm.predict(input_array)
                #print("Prediction: " + str(pred))
                await processor_queue.put(pred)

                if debug_prints: print("processor_coro: Made a prediction: " + str(pred))
        await uasyncio.sleep_ms(2000)
        