import logging
import builtins
import time
from queue import Queue
from threading import Thread, Event, Timer


class Source():

    DEFAULT_LENGTH = 1080

    def __init__(self, config, objectconfig, storage):
        # settings and parameters
        self.config = config
        self.objectconfig = objectconfig
        self.storage = storage

    def prepare(self):
        """
        gets called after all sources have been created, and before
        threads are started
        """
        pass

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
        try:
            value = cast(value)
            return value
        except ValueError:
            logging.debug("typecast error while casting {val} to {cast}".format(val=repr(value), cast=type_name))

    def push(self, value, timestamp=None, channel=None):
        if not channel:
            channel = self.get_config("name")
        if not timestamp:
            timestamp = time.time()
        value = self.typecast(value)
        length = self.get_config("values", Source.DEFAULT_LENGTH)
        self.storage.put(channel, timestamp, value, length)

    def pull(self, n=1, channel=None):
        """
        Pull timestamp-value-pairs from DB. By default just one,
        if n=0 all stored values. By default the configured name
        of the Source is used, another name can be set optionally.
        """
        if not channel:
            channel = self.get_config("name")
        return self.storage.get(channel, n)



class TimedSource(Source, Thread):

    def __init__(self, config, objectconfig, storage):
        super(TimedSource, self).__init__(config, objectconfig, storage)
        Thread.__init__(self)
        self.running = Event()
        self.running.set()
        self.interval = self.get_config("interval", 10)

    def run(self):
        self.timer_loop()

    def timer_loop(self):
        if self.running.is_set():
            self.timer = Timer(
                self.interval,
                self.timer_loop,
            )
            self.timer.start()
            self.poll()

    def cancel(self):
        self.running.clear()
        if self.timer is not None:
            self.timer.cancel()



class PubSubSource(Source, Thread):

    def __init__(self, config, objectconfig, storage):
        super(PubSubSource, self).__init__(config, objectconfig, storage)
        Thread.__init__(self)
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

    def callback(self, channel, timestamp, value):
        self.incoming.put((channel, timestamp, value))

    def cancel(self):
        self.running.clear()

    def run(self):
        while self.running.is_set():
            channel, timestamp, value = self.incoming.get()
            self.update(channel, timestamp, value)
