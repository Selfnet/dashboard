import logging
import builtins
import time
from asyncio import Event, Queue
import asyncio

from .worker import Worker


class Source(Worker):
    def __init__(self, config, objectconfig, storage):
        super(Source, self).__init__(config, objectconfig, storage)

    def get_channels(self):
        ''' return all channels that are written by this source '''
        if self.get_config("silent", False):
            return []
        return [self.get_config("name")]

    def typecast(self, value, default_type=None):
        ''' return the value typecasted to the type specified in the config '''
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

    async def push(self, value, timestamp=None, channel=None):
        if not channel:
            channel = self.get_config("name")
        if not timestamp:
            timestamp = time.time()
        value = self.typecast(value)
        length = self.get_config("values")
        await self.storage.put(channel, timestamp, value, length)

    async def pull(self, n=1, channel=None):
        """
        Pull timestamp-value-pairs from DB. By default just one,
        if n=0 all stored values. By default the configured name
        of the Source is used, another name can be set optionally.
        """
        if not channel:
            channel = self.get_config("name")
        return await self.storage.get(channel, n)


class TimedSource(Source):

    def __init__(self, config, objectconfig, storage):
        super(TimedSource, self).__init__(config, objectconfig, storage)
        self.interval = self.get_config("interval", 10)

    def cancel(self):
        self.running.clear()

    async def start(self):
        ''' Start async periodic acquisition of new values '''

        self.running = Event()
        self.running.set()
        asyncio.create_task(self.loop())

    async def loop(self):

        await asyncio.sleep(self.interval)
        if self.running.is_set():
            asyncio.create_task(self.loop())
            await self.poll()


class PubSubSource(Source):

    def __init__(self, config, objectconfig, storage):
        super(PubSubSource, self).__init__(config, objectconfig, storage)

    async def subscribe(self, mode="first"):
        mode = self.get_config("subscribe", mode)
        try:
            source = self.get_config("source")
            if isinstance(source, list):
                if mode == "first":
                    channels = [source[0]]
                elif mode == "all":
                    channels = source
                else:
                    raise KeyError("invalid PubSub subscribe mode")
            elif isinstance(source, str):
                channels = [source]
            for channel in channels:
                await self.storage.subscribe(channel, self.callback)
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                " - could not subscribe to channels"
            ]))

    async def callback(self, channel, timestamp, value):
        await self.incoming.put((channel, timestamp, value))

    def cancel(self):
        self.running.clear()

    async def start(self):

        self.incoming = Queue()
        self.running = Event()
        self.running.set()

        await self.subscribe()
        while self.running.is_set():
            channel, timestamp, value = await self.incoming.get()
            await self.update(channel, timestamp, value)
