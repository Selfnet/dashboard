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
                "channel": channel,
                "timestamp": timestamp,
                "value": value,
            },
        })
        self.write_message(response)

    def on_message(self, incoming_string):
        logging.debug('message received %s' % incoming_string)
        success = True
        incoming = json.loads(incoming_string)
        message = incoming.get("message", None)
        if message == "subscribe":
            channels = incoming.get("channels", [])
            if type(channels) == type(""):
                channels = [channels]
            self.listener.subscribe(self, channels)
        response = json.dumps({
            "message": "subscribe",
            "data": success,
        })
        self.write_message(response)

    def on_close(self):
        logging.debug('connection closed')
        self.listener.unsubscribe(self)
