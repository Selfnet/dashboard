from .base import PubSubSource



class Printer(PubSubSource):

    def update(self):
        for name in self.params["sources"]:
            last_ts = self.redis.lindex(name + ":ts", 0)
            last_val = self.redis.lindex(name + ":val", 0)
            print(last_ts + b" " + last_val)
