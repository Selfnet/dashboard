from asyncio import Lock, Event, Queue


class Storage:

    def __init__(self):
        self.storage = {}
        self.max_lens = {}
        self.callbacks = {}

    async def set_max_len(self, channel, length):
        """
        Set the default max_len for the named time-series.
        """
        async with self.max_lens_lock:
            self.max_lens[channel] = length

    async def subscribe(self, channel, callback):
        """
        Subscribe a callback function to a time-series. Every time, data
        gets added to the time-series, callback(channel, timestamp, value)
        is executed.
        """
        async with self.callbacks_lock:
            try:
                self.callbacks[channel].add(callback)
            except KeyError:
                self.callbacks[channel] = set([callback])

    async def unsubscribe(self, callback, channel=None):
        """
        Removes the given callback function from all time-series, if no
        channel is given. Otherwise the callback will be removed for only
        this time-series.
        """
        async with self.callbacks_lock:
            if channel:
                self.callbacks[channel].discard(callback)
            else:
                for channel in self.callbacks.keys():
                    self.callbacks[channel].discard(callback)

    async def put(self, channel, timestamp, value, max_len=None):
        """
        Append a data point to the named time-series. If max_len is set,
        or if the max_len for the named time-series has been set before,
        the time-series will be trucated to given number of entries.
        """
        await self.incoming.put((channel, timestamp, value, max_len))

    async def start(self):

        self.incoming = Queue()
        self.storage_lock = Lock()
        self.max_lens_lock = Lock()
        self.callbacks_lock = Lock()
        self.running = Event()
        self.running.set()

        while self.running.is_set():
            # blocks until an item is added:
            channel, timestamp, value, max_len = await self.incoming.get()
            if not max_len:
                try:
                    with self.max_lens_lock:
                        max_len = self.max_lens[channel]
                except KeyError:
                    # TODO: set a default max-length?
                    pass
            async with self.storage_lock:
                try:
                    self.storage[channel].append((timestamp, value))
                    if max_len and len(self.storage[channel]) > max_len:
                        self.storage[channel] = self.storage[channel][-max_len:]
                except KeyError:
                    self.storage[channel] = [(timestamp, value)]
            async with self.callbacks_lock:
                if channel in self.callbacks:
                    for callback in self.callbacks[channel]:
                        await callback(channel, timestamp, value)

    async def get(self, channel, n=1):
        """
        Retuns the last, or the last N elements of the named time-series.
        For N=0, all data points are returned.
        """
        async with self.storage_lock:
            try:
                result = self.storage[channel][-n:]
            except KeyError:
                result = []
        return result

    async def dump(self):
        async with self.storage_lock:
            # get a copy
            dump = dict(self.storage)
        return dump

    def load(self, data):
        self.storage = data
