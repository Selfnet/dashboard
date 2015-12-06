import logging
import threading
import redis
import time
import json
from .base import Source, PubSubSource
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler
from tornado.web import Application, RequestHandler



class Listener(threading.Thread):
    def __init__(self, db_config, channels):
        threading.Thread.__init__(self)
        self.redis = redis.Redis(**db_config)
        self.redis.config_set("notify-keyspace-events", "Kls")
        self.pubsub = None
        self.channels = channels
        self.subscribers = {}
        self.subscribers_lock = threading.Lock()
        self.start()

    def _get_channel_length(self, channel):
        # TODO
        #for source, channels in self.channels.items():
        #    if channel in channels:
        #        return source.get_config("values", Source.DEFAULT_LENGTH)
        return Source.DEFAULT_LENGTH

    def _channel_allowed(self, channel):
        if not self.channels: return True
        return channel in self.channels

    def _subscribe_pubsub(self, channel):
        channel_notify = "__keyspace@0__:" + channel + ":val"
        self.pubsub.subscribe(channel_notify)

    def subscribe(self, handler, channels):
        self.subscribers_lock.acquire()
        for channel in channels:
            if not self._channel_allowed(channel):
                continue
            if channel in self.subscribers:
                if handler not in self.subscribers.get(channel):
                    self.subscribers.get(channel).append(handler)
            else:
                self.subscribers[channel] = [handler]
                self._subscribe_pubsub(channel)
        self.subscribers_lock.release()

    def unsubscribe(self, handler):
        self.subscribers_lock.acquire()
        for ws in self.subscribers.values():
            while handler in ws:
                ws.remove(handler)
        self.subscribers_lock.release()

    def update(self, channel):
        timestamp = self.redis.lindex(channel + ":ts", 0).decode("utf-8")
        value = self.redis.lindex(channel + ":val", 0).decode("utf-8")
        self.subscribers_lock.acquire()
        handlers = self.subscribers.get(channel, [])
        for handler in handlers:
            handler.update(channel, timestamp, value)
        self.subscribers_lock.release()

    def history(self, channel, length=None):
        if (not isinstance(length, int)) or length <= 0:
            length = self._get_channel_length(channel)
        timestamps = [t.decode("utf-8") for t in self.redis.lrange(channel + ":ts", 0, length-1)]
        values = [v.decode("utf-8") for v in self.redis.lrange(channel + ":val", 0, length-1)]
        return dict(zip(timestamps, values))

    def run(self):
        while True:
            self.pubsub = self.redis.pubsub()
            if self.pubsub:
                for item in self.pubsub.listen():
                    if item["type"] == "message" and item["data"] == b"lpush" and item["channel"].endswith(b":val"):
                        # remove the __keyspace@0__: at the beginning and :val at the end
                        channel = ":".join(item["channel"].decode("utf-8").split(":")[1:-1])
                        self.update(channel)
            time.sleep(1)



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



class Websocket(Source, threading.Thread):

    def __init__(self, config, objectconfig):
        super().__init__(config, objectconfig)
        threading.Thread.__init__(self)

    def get_channels(self):
        return list()

    def run(self):
        # if no sources are configured, don't even try to start threads
        try:
            dbconfig = self.config["database"]
        except KeyError:
            logging.warning("No database config found, falling back to defaults.")
            dbconfig = {}

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

        listener = Listener(dbconfig, channels)

        # start websockets
        application = Application([
            (addr, WSHandler, dict(config=self.config, listener=listener)),
        ], debug=True)
        application.listen(port)

        IOLoop.instance().start()

    def cancel(self):
        # TODO
        pass
