from .base import PubSubSource



class Printer(PubSubSource):

    def update(self, item):
        for name in self.get_config("source"):
            last_ts, last_val = self.pull(name)[0]
            print(last_ts + b" " + last_val)
