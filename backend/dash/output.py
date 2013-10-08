import memcache
from time import time
import logging

class Memcache(object):
    def __init__(self, servers):
        self.mc = memcache.Client(servers, debug=0)
        self.meta = {}
        self.meta["started"] = int(time())

    def set_data(self, data):
        self.data = data

    def set_interval(self, interval):
        self.meta["interval"] = interval

    def set_published(self, published_sets):
        self.datasets = published_sets

    def run(self):
        self.meta["refresh"] = int(time())
        latest = {}
        history = {}
        for name in self.datasets:
            try:
                dataset = self.data.get_dataset(name)
                latest[name] = {"value": dataset.get(-1)}
                history[name] = {"values": dataset.get_list()}
            except IndexError:
                pass
        self.mc.set_multi({"meta": self.meta, "latest": latest, "history": history})

    def restore(self):
        """
        Restores previously stored data from memcached.
        The datapoints where no data was stored will
        be filled with None objects.
        Don't call this while updates are running.
        """
        logging.info("trying to restore from memache")
        try:
            last_update = self.mc.get("meta")["refresh"]
            history = self.mc.get("history")
        except KeyError:
            logging.warning("no valid data in memcache, can't restore")
            return
        now = int(time())
        padding = int((now - last_update) / self.meta["interval"])
        names = self.data.get_names()
        i = 0
        for name in names:
            # has history in memcache
            if name not in history:
                continue
            dataset = self.data.get_dataset(name)
            # last update still in dataset-length range?
            if dataset.length < padding:
                continue
            # insert history
            for value in history[name]["values"]:
                dataset.add(value)
            # insert padding
            for i in range(padding):
                dataset.add(None)
            i += 1
        logging.info("restored " + str(i) + " datasets (gap: " + str(now - last_update) + " seconds)")
        meta["refresh"] = int(time())
        self.mc.set_multi({"meta": meta})

