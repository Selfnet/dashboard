from threading import Thread, Lock, Event
from queue import Queue


class Storage(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.incoming = Queue()
        self.storage = {}
        self.storage_lock = Lock()
        self.max_lens = {}
        self.max_lens_lock = Lock()
        self.callbacks = {}
        self.callbacks_lock = Lock()
        self.running = Event()
        self.running.set()

    def set_max_len(self, name, length):
        """
        Set the default max_len for the named time-series.
        """
        with self.max_lens_lock:
            self.max_lens[name] = length

    def subscribe(self, name, callback):
        """
        Subscribe a callback function to a time-series. Every time, data
        gets added to the time-series, callback(name, timestamp, value)
        is executed.
        """
        with self.callbacks_lock:
            try:
                self.callbacks[name].add(callback)
            except KeyError:
                self.callbacks[name] = set([callback])

    def unsubscribe(self, callback, name=None):
        """
        Removes the given callback function from all time-series, if no
        name is given. Otherwise the callback will be removed for only
        this time-series.
        """
        with self.callbacks_lock:
            if name:
                self.callbacks[name].discard(callback)
            else:
                for name in self.callbacks.keys():
                    self.callbacks[name].discard(callback)

    def put(self, name, timestamp, value, max_len=None):
        """
        Append a data point to the named time-series. If max_len is set,
        or if the max_len for the named time-series has been set before,
        the time-series will be trucated to given number of entries.
        """
        self.incoming.put((name, timestamp, value, max_len))

    def run(self):
        while self.running.is_set():
            # blocks until an item is added:
            name, timestamp, value, max_len = self.incoming.get()
            if not max_len:
                try:
                    with self.max_lens_lock:
                        max_len = self.max_lens[name]
                except KeyError:
                    # TODO: set a default max-length?
                    pass
            with self.storage_lock:
                try:
                    self.storage[name].append((timestamp, value))
                    if max_len and len(self.storage[name]) > max_len:
                        self.storage[name] = self.storage[name][-max_len:]
                except KeyError:
                    self.storage[name] = [(timestamp, value)]
            with self.callbacks_lock:
                if name in self.callbacks:
                    for callback in self.callbacks[name]:
                        callback(name, timestamp, value)

    def get(self, name, n=1):
        """
        Retuns the last, or the last N elements of the named time-series.
        For N=0, all data points are returned.
        """
        with self.storage_lock:
            try:
                result = self.storage[name][-n:]
            except KeyError:
                result = []
        return result
