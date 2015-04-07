from tornado.wsgi import WSGIContainer
from tornado.websocket import WebSocketHandler
from tornado.web import RequestHandler
import logging
import json

class WebHandler(RequestHandler):
    def get(self):
        self.write("This app only handles the /websocket subdirectories. A index.html should be configured statically.")

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
                self.listener.subscribe(self, [channels])
            elif isinstance(channels, list):
                self.listener.subscribe(self, channels)
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
        logging.debug('connection closed')
        self.listener.unsubscribe(self)
