import logging
import time
import json
from .base.sources import Source
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler
from tornado.web import Application, RequestHandler
from queue import Queue
from threading import Thread, Lock, Event


class Listener(Source, Thread):

    def __init__(self, config, objectconfig, storage):
        super(Listener, self).__init__(config, objectconfig, storage)
        Thread.__init__(self)
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


class WSHandler(WebSocketHandler):
    def initialize(self, **kwargs):
        self.listener = kwargs["listener"]
        self.config = kwargs["config"]

    def check_origin(self, origin):
        return True

    def open(self):
        logging.debug('new connection')

    def update(self, channel, timestamp, value):
        response = json.dumps({
            "message": "update",
            "data": {
                channel: {
                    timestamp: value,
                },
            },
        })
        self.write_message(response)

    def on_message(self, incoming_string):
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
                self.listener.subscribe(channels, self.update)
            elif isinstance(channels, list):
                for channel in channels:
                    self.listener.subscribe(channel, self.update)
            else:
                # TODO log malformed request
                return
            response = json.dumps({
                "message": "subscribe",
                "data": True,
            })
            self.write_message(response)
        elif message == "history":
            requested = data
            channels = {}
            # "data": "some channel"
            if isinstance(requested, str):
                channels[requested] = self.listener.pull(name=requested, n=0)
            # "data": ["some channel", ... ]
            elif isinstance(requested, list):
                for channel in requested:
                    if not isinstance(channel, str):
                        # TODO log malformed request
                        return
                    channels[channel] = self.listener.pull(name=channel, n=0)
            # "data": {"some channel": {"length": "1337"}, ...}
            elif isinstance(requested, dict):
                for channel, settings in requested.items():
                    if (not isinstance(channel, str)):
                        # TODO log malformed request
                        return
                    length = settings.get("length")
                    length = int(length) if length != None else None
                    channels[channel] = self.listener.pull(name=channel, n=length)
            else:
                return
            response_dict = {
                "message": "history",
                "data": channels,
            }
            response = json.dumps(response_dict)
            self.write_message(response)

    def on_close(self):
        logging.debug('websocket connection closed')
        self.listener.unsubscribe(self.update)


class Websocket(Source, Thread):

    def __init__(self, config, objectconfig, storage):
        super().__init__(config, objectconfig, storage)
        Thread.__init__(self)

    def get_channels(self):
        return list()

    def run(self):
        permit = self.get_config("permit", "sources")
        addr   = self.get_config("address", "/websocket")
        port   = self.get_config("port", 5000)

        if permit == "sources":
            try:
                channels = self.get_config("source", None)
            except KeyError:
                logging.critical("Websocket needs configuration for \"source\" or \"permit: all\" statement")
                return
        elif permit == "all":
            channels = None

        if not channels:
            logging.warning("no websocket sources defined - allowing subscription for all channels")

        listener = Listener(self.config, self.objectconfig, self.storage)
        listener.start()

        # start websockets
        application = Application([
            (addr, WSHandler, dict(config=self.config, listener=listener)),
        ], debug=True)
        application.listen(port)

        IOLoop.instance().start()

    def cancel(self):
        # TODO
        pass
