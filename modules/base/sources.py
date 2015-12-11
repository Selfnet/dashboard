import threading
import logging
import builtins
import time
from queue import Queue
from threading import Lock, Event



class Source():

    DEFAULT_LENGTH = 1080

    def __init__(self, config, objectconfig, storage):
        # settings and parameters
        self.config = config
        self.objectconfig = objectconfig
        self.storage = storage

    def get_config(self, key, default=None):
        # priority 1: value is configured for this object
        try:
            value = self.objectconfig[key]
            return value
        except KeyError:
            # try again
            pass

        # priority 2: as class default
        try:
            # try to find the key in the defaults for this object type
            value = self.config["defaults"][self.__class__.__name__][key]
            return value
        except KeyError:
            # still nope
            pass

        # priority 3: value is configured as global default
        try:
            value = self.config["defaults"][key]
            return value
        except KeyError:
            # and again
            pass

        # still no luck? has something been set as hard-coded default?
        if default != None:
            return default

        # last measure
        raise KeyError("config parameter \"{key}\" not configured for {classname}".format(key=key, classname=self.__class__.__name__))

    def get_channels(self):
        "return all channels that are written by this source"
        if self.get_config("silent", False):
            return []
        return [self.get_config("name")]

    def typecast(self, value, default_type=None):
        try:
            type_name = self.get_config("typecast", default_type)
        except KeyError:
            return value
        try:
            cast = getattr(builtins, type_name)
            if not isinstance(cast, type):
                raise ValueError("not a type")
        except ValueError:
            raise Exception("invalid type cast (\"{type_name}\" not a built-in type) for {classname}".format(type_name=type_name, classname=self.__class__.__name__))
        return cast(value)

    def push(self, value, timestamp=None, name=None):
        if not name:
            name = self.get_config("name")
        if not timestamp:
            timestamp = time.time()
        value = self.typecast(value)
        length = self.get_config("values", Source.DEFAULT_LENGTH)
        self.storage.put(name, timestamp, value, length)

    def pull(self, n=1, name=None):
        """
        Pull timestamp-value-pairs from DB. By default just one,
        if n=0 all stored values. By default the configured name
        of the Source is used, another name can be set optionally.
        """
        if not name:
            name = self.get_config("name")
        return self.storage.get(name, n)



class TimedSource(Source, threading.Thread):

    def __init__(self, config, objectconfig, storage):
        super(TimedSource, self).__init__(config, objectconfig, storage)
        threading.Thread.__init__(self)
        self.running = threading.Event()
        self.running.set()
        self.interval = self.get_config("interval", 10)

    def run(self):
        self.timer_loop()

    def timer_loop(self):
        if self.running.is_set():
            self.timer = threading.Timer(
                self.interval,
                self.timer_loop,
            )
            self.timer.start()
            self.poll()

    def cancel(self):
        self.running.clear()
        if self.timer is not None:
            self.timer.cancel()



class PubSubSource(Source, threading.Thread):

    def __init__(self, config, objectconfig, storage):
        super(PubSubSource, self).__init__(config, objectconfig, storage)
        threading.Thread.__init__(self)
        self.incoming = Queue()
        self.running = Event()
        self.running.set()
        self.subscribe()

    def subscribe(self, mode="first"):
        mode = self.get_config("subscribe", mode)
        try:
            source = self.get_config("source")
            if type(source) == type([]):
                if mode == "first":
                    channels = [source[0]]
                elif mode == "all":
                    channels = [source]
                else:
                    raise KeyError("invalid PubSub subscribe mode")
            elif type(source) == type(""):
                channels = [source]
            for channel in channels:
                self.storage.subscribe(channel, self.callback)
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                " - could not subscribe to channels"
            ]))

    def callback(self, name, timestamp, value):
        self.incoming.put((name, timestamp, value))

    def cancel(self):
        self.running.clear()

    def run(self):
        while self.running.is_set():
            name, timestamp, value = self.incoming.get()
            self.update(name, timestamp, value)


class Listener(Source, threading.Thread):

    def __init__(self, config, objectconfig, storage):
        super(Listener, self).__init__(config, objectconfig, storage)
        threading.Thread.__init__(self)
        self.incoming = Queue()
        self.callbacks = {}
        self.callbacks_lock = Lock()
        self.running = Event()
        self.running.set()

    def subscribe(self, channel, callback):
        with self.callbacks_lock:
            try:
                self.callbacks[channel].add(callback)
            except KeyError:
                self.callbacks[channel] = set([callback])
        self.storage.subscribe(channel, self.callback)

    def unsubscribe(self, callback):
        with self.callbacks_lock:
            for channel in self.callbacks.keys():
                self.callbacks[channel].discard(callback)
                if len(self.callbacks[channel]) == 0:
                    self.storage.unsubscribe(self.callback, name=channel)

    def callback(self, name, timestamp, value):
        self.incoming.put((name, timestamp, value))

    def cancel(self):
        self.running.clear()

    def run(self):
        while self.running.is_set():
            name, timestamp, value = self.incoming.get()
            with self.callbacks_lock:
                if name in self.callbacks.keys():
                    for callback in self.callbacks[name]:
                        callback(name, timestamp, value)
