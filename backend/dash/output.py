import memcache
from time import time

class Memcache(object):
    def __init__(self, servers, config):
        self.mc = memcache.Client(servers, debug=0)
        self.meta = {}
        self.meta["started"] = int(time())
        self.meta["interval"] = config.interval
        self.config = config

    def run(self):
        datasets = self.config.get_published()
        self.meta["refresh"] = int(time())
        latest = {}
        history = {}
        for name in datasets:
            try:
                latest[name] = datasets[name][-1]
                history[name] = {"unit": "loltest", "values": datasets[name]}
            except IndexError:
                pass
        self.mc.set_multi({"meta": self.meta, "latest": latest, "history": history})

