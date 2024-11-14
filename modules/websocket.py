import logging
import json
from .base.worker import Worker
from asyncio import Lock, Event, Queue
import asyncio
import websockets
import datetime


class Listener:

    def __init__(self, storage):
        self.storage = storage

    async def subscribe(self, channel, callback):
        async with self.callbacks_lock:
            try:
                self.callbacks[channel].add(callback)
            except KeyError:
                self.callbacks[channel] = set([callback])
        await self.storage.subscribe(channel, self.callback)

    async def unsubscribe(self, callback):
        async with self.callbacks_lock:
            for channel in self.callbacks.keys():
                self.callbacks[channel].discard(callback)
                if len(self.callbacks[channel]) == 0:
                    await self.storage.unsubscribe(self.callback, channel=channel)

    async def callback(self, name, timestamp, value):
        await self.incoming.put((name, timestamp, value))

    def cancel(self):
        self.running.clear()

    async def start(self):
        self.incoming = Queue()
        self.callbacks = {}
        self.callbacks_lock = Lock()
        self.running = Event()
        self.running.set()
        while self.running.is_set():
            name, timestamp, value = await self.incoming.get()
            async with self.callbacks_lock:
                if name in self.callbacks.keys():
                    for callback in self.callbacks[name]:
                        await callback(name, timestamp, value)


class WSHandler:
    def __init__(self, listener, storage):
        self.listener = listener
        self.storage = storage

    def check_origin(self, origin):
        return True

    async def update(self, channel, timestamp, value):
        response = json.dumps({
            "message": "update",
            "data": {
                channel: {
                    timestamp: value,
                },
            },
        })
        await self.write_message(response)

    async def on_message(self, incoming_string):
        logging.debug('message received %s' % incoming_string)
        try:
            incoming = json.loads(incoming_string)
        except ValueError:
            # invalid JSON
            return
        message = incoming.get("message", None)
        data = incoming.get("data", [])
        if message == "subscribe":
            channels = data
            if isinstance(channels, str):
                await self.listener.subscribe(channels, self.update)
            elif isinstance(channels, list):
                for channel in channels:
                    await self.listener.subscribe(channel, self.update)
            else:
                # TODO log malformed request
                return
            response = json.dumps({
                "message": "subscribe",
                "data": True,
            })
            await self.write_message(response)
        elif message == "history":
            requested = data
            channels = {}
            # "data": "some channel"
            if isinstance(requested, str):
                channels[requested] = await self.storage.get(channel=requested, n=0)
            # "data": ["some channel", ... ]
            elif isinstance(requested, list):
                for channel in requested:
                    if not isinstance(channel, str):
                        # TODO log malformed request
                        return
                    channels[channel] = await self.storage.get(channel=channel, n=0)
            # "data": {"some channel": {"length": "1337"}, ...}
            elif isinstance(requested, dict):
                for channel, settings in requested.items():
                    if (not isinstance(channel, str)):
                        # TODO log malformed request
                        return
                    length = settings.get("length")
                    length = int(length) if length is not None else None
                    channels[channel] = await self.storage.get(channel=channel, n=length)
            else:
                return
            response_dict = {
                "message": "history",
                "data": channels,
            }
            response = json.dumps(response_dict)
            await self.write_message(response)

    async def start(self, websocket):
        ''' Loop for Websocket '''

        logging.debug('new connection')

        self.websocket = websocket

        try:
            async for message in websocket:
                await self.on_message(message)
        finally:
            logging.debug('websocket connection closed')
            await self.listener.unsubscribe(self.update)

    async def write_message(self, response):
        logging.info(datetime.datetime.now().isoformat() + ' ' + 'Writing response ' + str(response))
        await self.websocket.send(response)


class Websocket(Worker):

    def __init__(self, config, objectconfig, storage):
        super(Websocket, self).__init__(config, objectconfig, storage)

    def get_channels(self):
        return list()

    def prepare(self):
        self.permit = self.get_config("permit", "sources")
        self.addr = self.get_config("address", "")
        self.port = self.get_config("port", 5000)

        if self.permit == "sources":
            try:
                self.channels = self.get_config("source", None)
            except KeyError:
                logging.critical("Websocket needs configuration for \"source\" or \"permit: all\" statement")
                return
        elif self.permit == "all":
            self.channels = None

        if not self.channels:
            logging.warning("no websocket sources defined - allowing subscription for all channels")

        self.listener = Listener(self.storage)

    async def start(self):
        logging.info('Starting Websocket')
        # start websockets
        asyncio.create_task(self.listener.start())
        await websockets.serve(WSHandler(self.listener, self.storage).start, self.addr, self.port)

    def cancel(self):
        # TODO
        pass
