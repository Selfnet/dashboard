import threading
import logging
import time
import redis



class Source():

    settings = {
        "db": {
            # database settings
            "host": "localhost",
            "port": 6379,
        },
        # number of stored values
        "length": 60,

        # seconds between two runs
        "interval": 60,
    }

    defaults = {}

    def __init__(self, **kwargs):
        # settings and parameters
        self.params = {}  
        self.params.update(self.settings)
        self.params.update(self.defaults)
        self.params.update(kwargs)

        # check if all required arguments are given
        for key in self.required:
            if key not in self.params:
                raise ValueError("%s argument is required" % key)

        self.connect_db()

    def connect_db(self):
        self.redis = redis.Redis(**self.settings["db"])

    def push(self, name, value, timestamp=None):
        if not timestamp:
            timestamp = time.time()
        length = self.params["length"]
        name = self.params["name"]
        try:
            self.redis.lpush(name + ":val", value)
            self.redis.ltrim(name + ":val", 0, length - 1)
            self.redis.lpush(name + ":ts", timestamp)
            self.redis.ltrim(name + ":ts", 0, length - 1)
        except Exception as e:
            logging.error(" ".join([
                type(e).__name__ + ":",
                str(e),
                " - could not write to redis database"
            ])



class TimedSource(Source, threading.Thread):

    def __init__(self, **kwargs):
        super(OriginalSource, self).__init__(**kwargs)
        threading.Thread.__init__(self)
        self.running = threading.Event()
        self.running.set()
        self.start()

    def run(self):
        while self.running.is_set():
            self.timer = threading.Timer(
                self.params["interval"],
                self.poll,
            )
            self.timer.start()
            self.timer.join()

    def cancel(self):
        self.running.clear()
        if self.timer is not None:
            self.timer.cancel()



class PubSubSource(Source, threading.Thread):
    def __init__(self, **kwargs):
        super(PubSubSource, self).__init__(**kwargs)
        threading.Thread.__init__(self)
        self.pubsub = self.redis.pubsub()
        channels = ["__keyspace@0__:" + s + ":val" for s in self.params["sources"]]
        self.pubsub.subscribe(channels)
        self.start()

    def cancel(self):
        self.pubsub.close()

    def run(self):
        for item in self.pubsub.listen():
            if item["type"] == "message" and item["data"] == b"lpush":
                self.work()
