import threading
import redis
import time
import logging
from sources.base import Source

class Listener(threading.Thread):
    def __init__(self, db_config, channels):
        threading.Thread.__init__(self)
        self.redis = redis.Redis(**db_config)
        self.redis.config_set("notify-keyspace-events", "Kls")
        self.channels = channels
        self.subscribers = {}
        self.subscribers_lock = threading.Lock()
        self.start()

    def _get_channel_length(self, channel):
        for source, channels in self.channels.items():
            if channel in channels:
                return source.get_config("values", Source.DEFAULT_LENGTH)
        return Source.DEFAULT_LENGTH

    def _channel_allowed(self, channel):
        for channels in self.channels.values():
            if channel in channels:
                return True
        return False

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
            pubsub = self.redis.pubsub()
            channels = set()
            for channels_per_source in self.channels.values():
                for channel in channels_per_source:
                    channels.add(channel)
            channels = ["__keyspace@0__:" + channel + ":val" for channel in channels]
            pubsub.subscribe(channels)
            if pubsub:
                for item in pubsub.listen():
                    if item["type"] == "message" and item["data"] == b"lpush" and item["channel"].endswith(b":val"):
                        # remove the __keyspace@0__: at the beginning and :val at the end
                        channel = ":".join(item["channel"].decode("utf-8").split(":")[1:-1])
                        self.update(channel)
            time.sleep(1)
