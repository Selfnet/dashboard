import threading
import redis
import time
import logging

class Listener(threading.Thread):
    def __init__(self, db_config, channels):
        threading.Thread.__init__(self)
        self.redis = redis.Redis(**db_config)
        self.redis.config_set("notify-keyspace-events", "Kls")
        self.channels = channels
        self.subscribers = {}
        self.subscribers_lock = threading.Lock()
        self.start()

    def subscribe(self, handler, channels):
        self.subscribers_lock.acquire()
        for channel in channels:
            if channel not in self.channels:
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
        timestamp = self.redis.lindex(channel + ":ts", 0)
        value = self.redis.lindex(channel + ":val", 0)
        self.subscribers_lock.acquire()
        handlers = self.subscribers.get(channel, [])
        for handler in handlers:
            handler.update(channel, timestamp, value)
        self.subscribers_lock.release()

    def history(self, channel, length=None):
        if channel not in self.channels:
            return
        if type(length) != int or length <= 0:
            length = 1080  # default: 3 hours of data at 10sec intervals
        timestamps = self.redis.lrange(channel + ":ts", 0, length-1)
        values = self.redis.lrange(channel + ":val", 0, length-1)
        return dict(zip(timestamps, values))

    def run(self):
        while True:
            pubsub = self.redis.pubsub()
            channels = ["__keyspace@0__:" + channel + ":val" for channel in self.channels]
            pubsub.subscribe(channels)
            if pubsub:
                for item in pubsub.listen():
                    if item["type"] == "message" and item["data"] == b"lpush" and item["channel"].endswith(b":val"):
                        # remove the __keyspace@0__: at the beginning and :val at the end
                        channel = ":".join(str(item["channel"]).split(":")[1:-1])
                        self.update(channel)
            time.sleep(1)
