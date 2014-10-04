import threading
import logging
import time
import redis



class Source():

    def __init__(self, config, objectconfig):
        # settings and parameters
        self.config = config
        self.objectconfig = objectconfig
        self.connect_db()

    def get_config(self, key, default=None):
        # priority 1: value is configured for this object
        try:
            value = self.objectconfig[key]
            return value
        except KeyError:
            # try again
            pass

        # priority 2: as class default
        try:
            # try to find the key in the defaults for this object type
            value = self.config["defaults"][self.__class__.__name__][key]
            return value
        except KeyError:
            # still nope
            pass

        # priority 3: value is configured as global default
        try:
            value = self.config["defaults"][key]
            return value
        except KeyError:
            # and again
            pass

        # still no luck? has something been set as hard-coded default?
        if default != None:
            return default

        # last measure
        raise KeyError("config parameter \"{key}\" not configured for {classname}".format(key=key, classname=self.__class__.__name__))

    def connect_db(self):
        try:
            dbconfig = self.config["database"]
        except KeyError:
            raise KeyError("no database config found")
        try:
            self.redis = redis.Redis(**dbconfig)
        except Exception as e:
            logging.error(" ".join([
                type(e).__name__ + ":",
                str(e),
                " - could not write to redis database"
            ]))

    def push(self, name, value, timestamp=None):
        if not timestamp:
            timestamp = time.time()
        length = self.get_config("values", 1080)
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
            ]))



class TimedSource(Source, threading.Thread):

    def __init__(self, config, objectconfig):
        super(TimedSource, self).__init__(config, objectconfig)
        threading.Thread.__init__(self)
        self.running = threading.Event()
        self.running.set()

    def run(self):
        while self.running.is_set():
            interval = self.get_config("interval", 10)
            self.timer = threading.Timer(
                interval,
                self.poll,
            )
            self.timer.start()
            self.timer.join()

    def cancel(self):
        self.running.clear()
        if self.timer is not None:
            self.timer.cancel()



class PubSubSource(Source, threading.Thread):

    def __init__(self, config, objectconfig):
        super(PubSubSource, self).__init__(config, objectconfig)
        threading.Thread.__init__(self)
        self.pubsub = None
        self.subscribe()

    def subscribe(self):
        try:
            self.redis.config_set("notify-keyspace-events", "Kls")
            self.pubsub = self.redis.pubsub()
            sources = self.get_config("sources")
            if not sources:
                raise Exception("no source datasets configured for PubSubSource")
            channels = ["__keyspace@0__:" + s + ":val" for s in sources]
            self.pubsub.subscribe(channels)
        except Exception as e:
            logging.error(" ".join([
                type(e).__name__ + ":",
                str(e),
                " - could not subscribe to channels on redis database"
            ]))

    def cancel(self):
        self.pubsub.close()

    def run(self):
        while True:
            if self.pubsub:
                for item in self.pubsub.listen():
                    if item["type"] == "message" and item["data"] == b"lpush":
                        self.update()
            time.sleep(1)
