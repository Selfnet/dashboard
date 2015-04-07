import threading
import logging
#import builtins
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

    def get_channels(self):
        "return all channels that are written by this source"
        if self.get_config("silent", False):
            return []
        return [self.get_config("name")]

    def typecast(self, value, default_type=None):
        try:
            type_name = self.get_config("typecast", default_type)
        except KeyError:
            return value
        try:
            cast = getattr(builtins, type_name)
            if not isinstance(cast, type):
                raise ValueError("not a type")
        except ValueError:
            raise Exception("HTTPGet: invalid type cast (not a built-in type)")
        return cast(value)

    def connect_db(self):
        try:
            dbconfig = self.config["database"]
        except KeyError:
            logging.warning("No database config found, falling back to defaults.")
            dbconfig = {}
        try:
            self.redis = redis.Redis(**dbconfig)
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                " - could not write to redis database"
            ]))

    def push(self, value, timestamp=None, name=None):
        if not name:
            name = self.get_config("name")
        if not timestamp:
            timestamp = time.time()
        value = self.typecast(value)
        length = self.get_config("values", 1080)
        try:
            self.redis.lpush(name + ":ts", timestamp)
            self.redis.ltrim(name + ":ts", 0, length - 1)
            self.redis.lpush(name + ":val", value)
            self.redis.ltrim(name + ":val", 0, length - 1)
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                " - could not write to redis database"
            ]))

    def pull(self, n=1, name=None):
        if not name:
            name = self.get_config("name")
        ts = self.redis.lrange(name + ":ts", 0, n-1)
        val = self.redis.lrange(name + ":val", 0, n-1)
        return list(zip(ts, val))



class TimedSource(Source, threading.Thread):

    def __init__(self, config, objectconfig):
        super(TimedSource, self).__init__(config, objectconfig)
        threading.Thread.__init__(self)
        self.running = threading.Event()
        self.running.set()
        self.interval = self.get_config("interval", 10)

    def run(self):
        self.timer_loop()

    def timer_loop(self):
        if self.running.is_set():
            self.timer = threading.Timer(
                self.interval,
                self.timer_loop,
            )
            self.timer.start()
            self.poll()

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
        mode = self.get_config("subscribe", "first")
        try:
            self.redis.config_set("notify-keyspace-events", "Kls")
            self.pubsub = self.redis.pubsub()
            source = self.get_config("source")
            if type(source) == type([]):
                if mode == "first":
                    channels = ["__keyspace@0__:" + source[0] + ":val"]
                elif mode == "all":
                    channels = ["__keyspace@0__:" + s + ":val" for s in source]
                else:
                    raise KeyError("invalid PubSub subscribe mode")
            elif type(source) == type(""):
                channels = ["__keyspace@0__:" + source + ":val"]
            self.pubsub.subscribe(channels)
        except Exception as e:
            logging.exception(" ".join([
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
                    if item["type"] == "message" and item["data"] == "lpush":
                        self.update()
            time.sleep(1)
