import logging
import threading
import time
import json
from .base.sources import Source, Listener
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler
from tornado.web import Application, RequestHandler


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
                channels[requested] = self.listener.history(requested)
            # "data": ["some channel", ... ]
            elif isinstance(requested, list):
                for channel in requested:
                    if not isinstance(channel, str):
                        # TODO log malformed request
                        return
                    channels[channel] = self.listener.history(channel)
            # "data": {"some channel": {"length": "1337"}, ...}
            elif isinstance(requested, dict):
                for channel, settings in requested.items():
                    if (not isinstance(channel, str)):
                        # TODO log malformed request
                        return
                    length = settings.get("length")
                    length = int(length) if length != None else None
                    channels[channel] = self.listener.history(channel, length)
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


class Websocket(Source, threading.Thread):

    def __init__(self, config, objectconfig, storage):
        super().__init__(config, objectconfig, storage)
        threading.Thread.__init__(self)

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
