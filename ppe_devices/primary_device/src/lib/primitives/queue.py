# queue.py: adapted from uasyncio V2

# Copyright (c) 2018-2020 Peter Hinch
# Released under the MIT License (MIT) - see LICENSE file

# Code is based on Paul Sokolovsky's work.
# This is a temporary solution until uasyncio V3 gets an efficient official version

import uasyncio as asyncio


# Exception raised by get_nowait().
class QueueEmpty(Exception):
    pass


# Exception raised by put_nowait().
class QueueFull(Exception):
    pass

class Queue:
    """FIFO queue."""

    def __init__(self, maxsize=0):
        """!
        Constructor for a FIFO queue.
        
        @param maxsize Maximum queue length.
        """
        self.maxsize = maxsize
        self._queue = []
        self._evput = asyncio.Event()  # Triggered by put, tested by get
        self._evget = asyncio.Event()  # Triggered by get, tested by put

    def _get(self):
        self._evget.set()  # Schedule all tasks waiting on get
        self._evget.clear()
        return self._queue.pop(0)

    async def get(self):
        """!
        Asynchronously get an item form the queue.
        
        Usage: item = await queue.get().
        May be multiple tasks waiting on get().
        If queue is empty, suspend task until a put occurs.
        """
        while self.empty():
            await self._evput.wait()
        return self._get()

    def get_nowait(self):  # Remove and return an item from the queue.
        # Return an item if one is immediately available, else raise QueueEmpty.
        if self.empty():
            raise QueueEmpty()
        return self._get()

    def _put(self, val):
        self._evput.set()  # Schedule tasks waiting on put
        self._evput.clear()
        self._queue.append(val)

    async def put(self, val):
        """!
        Asynchronously put an item into the queue.
        
        Usage: item = await queue.put(item).
        If queue is full, suspend task until a get occurs.
        """
        while self.full():
            await self._evget.wait()
        self._put(val)

    def put_nowait(self, val):  # Put an item into the queue without blocking.
        if self.full():
            raise QueueFull()
        self._put(val)

    def qsize(self):  # Number of items in the queue.
        return len(self._queue)

    def empty(self):  # Return True if the queue is empty, False otherwise.
        return len(self._queue) == 0

    def full(self):  # Return True if there are maxsize items in the queue.
        # Note: if the Queue was initialized with maxsize=0 (the default) or
        # any negative number, then full() is never True.
        return self.maxsize > 0 and self.qsize() >= self.maxsize
