import time
import uasyncio
from lib.rssi_circular_buffer import WindowedCircularBuffer
from models import events
from models.devices import Level2Device
from lib.primitives.queue import Queue

class ProcessableEntity:
    """Abstract class for a processable entity.

    A processable entity is an entity that can be processed by the preprocessor.
    A processable entity is composed of one or more raw devices, and has at least one
    method to trigger the preprocessing of the raw data.
    """
    def __init__(self, raw_devices: list[Level2Device]):
        self.raw_devices = raw_devices
        self.raw_device_names = [d.get_name() for d in self.raw_devices]
    
    # abstract method
    def trigger_preprocessing(self):
        """Trigger the preprocessing of the raw data."""
        pass

class Helmet(ProcessableEntity):
    """Class for the Helmet object.
    
    The Helmet object is composed of one raw device only (the Level2Device 
    corresponding to the helmet device).

    The preprocessing of the Helmet object is done as follows:
    - the count of raw data in the last time window is computed
    - the average RSSI of the last time window is computed
    - the variance of the averaged windowed data is computed
    - the standard deviation of the averaged windowed data is computed
    """
    def __init__(self, raw_devices: list[Level2Device]):
        # List of raw devices
        self.raw_devices = raw_devices
        # List of raw devices names
        self.raw_device_names = [d.get_name() for d in self.raw_devices]

        # The Helmet class requires only one raw device
        if len(self.raw_devices) != 1:
            print("Helmet: invalid number of raw devices")
            return
        
        # Count of raw data in the last time window
        self._count_raw = None
        # Buffer of averaged windowed data
        self._avg_buffer = WindowedCircularBuffer(
            max_size=50,
            time_window_s=5
            )
        # Variance of the averaged windowed data
        self._avg_variance = None
        # Standard deviation of the averaged windowed data
        self._avg_std_dev = None

    def trigger_preprocessing(self):
        """Trigger the preprocessing of the raw data."""
        # Update the count of raw data in the last time window
        self._count_raw = self.raw_devices[0].get_count()
        # Add the last averaged window to the avg buffer
        self._avg_buffer.append(self.raw_devices[0].get_rssi()[0], time.ticks_ms())

        # Update the variance of the averaged windowed data
        # self._avg_variance = self._avg_buffer.get_window_variance()[0]
        # Update the standard deviation of the averaged windowed data
        # self._avg_std_dev = self._avg_buffer.get_window_std_dev()[0]
    
    def get_statistics(self):
        """Return the statistics of the Helmet object.

        The tuple is composed as follows:
        - count of raw data in the last time window
        - average RSSI of the last time window
        - variance of the averaged windowed data
        - standard deviation of the averaged windowed data
        """    
        avg, count = self._avg_buffer.get_window_avg()
        variance, std_dev, _ = self._avg_buffer.get_window_var_std_dev()
        return (count, avg, variance, std_dev)

class Shoes(ProcessableEntity):
    """Class for the Shoes object.
    
    The Shoes object is composed of two raw devices (the Level2Devices
    corresponding to the left and right shoes).
    
    The preprocessing of the Shoes object is done as follows:
    - the average RSSI of the last time window is computed for each shoe
    - the average RSSI of the last time window is computed for both shoes 
      using the average of the two averages above
    - the variance of the averaged windowed data is computed
    - the standard deviation of the averaged windowed data is computed
    """
    def __init__(self, raw_devices: list[Level2Device] = []):
        self.raw_devices = raw_devices
        self.raw_device_names = [d.get_name() for d in self.raw_devices]

        # Count of raw data in the last time window. We pick the minimum count between the two shoes
        self._count_raw = None
        # Buffer of averaged windowed data for the left shoe
        self._avg_buffer_left = WindowedCircularBuffer(
            max_size=50,
            time_window_s=5
            )
        # Buffer of averaged windowed data for the right shoe
        self._avg_buffer_right = WindowedCircularBuffer(
            max_size=50,
            time_window_s=5
            )
        # Buffer of averaged windowed data for both shoes, computed as the average of the two buffers above
        self._avg_buffer_both = WindowedCircularBuffer(
            max_size=50,
            time_window_s=5
            )
        # Variance of the averaged windowed data for both shoes
        self._avg_variance = None
        # Standard deviation of the averaged windowed data for both shoes
        self._avg_std_dev = None
        
    def check_raw_devices(self):
        """Check if the number of raw devices is correct."""
        # The Shoes class requires two raw devices
        if len(self.raw_devices) != 2:
            print("Shoes: invalid number of raw devices")
            return False
        return True
    
    def add_raw_device(self, raw_device: Level2Device):
        """Add a raw device to the Shoes object."""
        if not self.check_raw_devices():
            self.raw_devices.append(raw_device)
            self.raw_device_names.append(raw_device.get_name())
        else:
            print("Shoes: cannot add raw device")
    
    def trigger_preprocessing(self):
        """Trigger the preprocessing of the raw data."""
        # Update the count of raw data in the last time window
        self._count_raw = min(self.raw_devices[0].get_count(), self.raw_devices[1].get_count())
        
        # Add the last averaged window to the avg buffer for the left shoe
        temp = self.raw_devices[0].get_rssi()[0]
        if temp is None:
            pass
        else:
            self._avg_buffer_left.append(temp, time.ticks_ms())
        # Add the last averaged window to the avg buffer for the right shoe
        temp = self.raw_devices[1].get_rssi()[0]
        if temp is None:
            pass
        else:
            self._avg_buffer_right.append(temp, time.ticks_ms())
        
        # Compute the average of the two buffers above and add it to the avg buffer for both shoes
        if self._avg_buffer_left.get_window_avg()[0] == None and self._avg_buffer_right.get_window_avg()[0] == None:
            pass        
        
        elif self._avg_buffer_left.get_window_avg()[0] == None:
            self._avg_buffer_both.append(self._avg_buffer_right.get_window_avg()[0], time.ticks_ms())
            
        elif self._avg_buffer_right.get_window_avg()[0] == None:
            self._avg_buffer_both.append(self._avg_buffer_left.get_window_avg()[0], time.ticks_ms())
            
        else:
            self._avg_buffer_both.append(
                (self._avg_buffer_left.get_window_avg()[0]+self._avg_buffer_right.get_window_avg()[0])/2,
                time.ticks_ms()
                )
        
        # Update the variance of the averaged windowed data
        #self._avg_variance = self._avg_buffer_both.get_window_variance()[0]
        # Update the standard deviation of the averaged windowed data
        #self._avg_std_dev = self._avg_buffer_both.get_window_std_dev()[0]

    def get_statistics(self):
        """Return the statistics of the Shoes object.
        The tuple is composed as follows:
        - count of raw data in the last time window (minimum between the two shoes)
        - average RSSI of the last averaged time window (average between the two shoes averadges)
        - variance of the averaged windowed data
        - standard deviation of the averaged windowed data
        """
        avg, count = self._avg_buffer_both.get_window_avg()
        variance, std_dev, _ = self._avg_buffer_both.get_window_var_std_dev()
        return (count, avg, variance, std_dev)

async def preprocessor_coro(
        dev_to_process: list(Level2Device), 
        preprocessor_queue: Queue,
        processables: list
        ):
    """Preprocessor coroutine.
    
    This coroutine carries out the preprocessing of data received from the BLE devices.
    """
    # Initialize the useful data structures
    shoes = Shoes()
    for dev in dev_to_process:
        if dev.get_type() == "helmet":
            helmet = Helmet(raw_devices=[dev])
        elif dev.get_type() == "shoe_dx":
            shoes.add_raw_device(dev)
        elif dev.get_type() == "shoe_sx":
            shoes.add_raw_device(dev)
        else:
            print("preprocessor_coro: invalid device type")
            return
    
    processables.append(helmet)
    processables.append(shoes)

    while True:
        dev_name = await preprocessor_queue.get()
        # Trigger the preprocessing for the processable entities that have the device with the given name
        for p in processables:
            if dev_name in p.raw_device_names:
                p.trigger_preprocessing()
                break
        