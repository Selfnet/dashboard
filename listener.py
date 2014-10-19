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
        # TODO check if channels are configured and not silent
        self.subscribers_lock.acquire()
        for channel in channels:
            if channel in self.subscribers:
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
        # TODO remove
        logging.debug("updating channel " + channel)
        timestamp = self.redis.lindex(channel + ":ts", 0)
        value = self.redis.lindex(channel + ":val", 0)
        self.subscribers_lock.acquire()
        handlers = self.subscribers.get(channel, [])
        for handler in handlers:
            handler.update(channel, timestamp, value)
        self.subscribers_lock.release()

    def run(self):
        while True:
            pubsub = self.redis.pubsub()
            channels = ["__keyspace@0__:" + channel + ":val" for channel in self.channels]
            pubsub.subscribe(channels)
            if pubsub:
                for item in pubsub.listen():
                    if item["type"] == "message" and item["data"] == "lpush" and item["channel"].endswith(":val"):
                        # remove the __keyspace@0__: at the beginning and :val at the end
                        channel = ":".join(item["channel"].split(":")[1:-1])
                        self.update(channel)
            time.sleep(1)
