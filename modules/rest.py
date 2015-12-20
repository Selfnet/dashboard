import logging
import time
import json
from .base.sources import Source
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler, HTTPError, asynchronous
from queue import Queue
from threading import Thread, Lock, Event


class Getter(Thread):

    def __init__(self, storage):
        Thread.__init__(self)
        self.storage = storage
        self.jobs = Queue()
        self.running = Event()
        self.running.set()

    def get(self, channels, n, time_min, time_max, callback):
        self.jobs.put((channels, n, time_min, time_max, callback))

    def run(self):
        while self.running.is_set():
            channels, n, time_min, time_max, callback = self.jobs.get()
            datasets = {}
            for channel in channels:
                datasets[channel] = self.storage.get(channel=channel, n=n)
                if time_min:
                    datasets[channel] = [(ts, val) for ts, val in datasets[channel] if ts > time_min]
                if time_max:
                    datasets[channel] = [(ts, val) for ts, val in datasets[channel] if ts < time_max]
            response_dict = {
                # TODO
                # "meta": {
                #     "channels" = channels,
                #     "time_min" = time_min,
                #     "time_max" = time_max,
                #     "number"   = number,
                # },
                "data": datasets,
            }
            response = json.dumps(response_dict)
            callback(response)


class RESTHandler(RequestHandler):
    def initialize(self, **kwargs):
        self.getter = kwargs["getter"]
        self.config = kwargs["config"]

    @asynchronous
    def get(self):
        channels = self.get_argument("channels",  "")
        time_min = self.get_argument("time_min", "")
        time_max = self.get_argument("time_max", "")
        last = self.get_argument("last",   "")
        datasets = {}
        channels = channels.split(",")

        try:
            time_min = int(time_min)
        except ValueError:
            time_min = None

        try:
            time_max = int(time_max)
        except ValueError:
            time_max = None

        try:
            last = int(last)
        except ValueError:
            last = 0

        self.getter.get(
            channels=channels,
            n=last,
            time_min=time_min,
            time_max=time_max,
            callback=self.callback
        )

    def callback(self, response):
        self.write(response)
        self.finish()


class REST(Source, Thread):

    def __init__(self, config, objectconfig, storage):
        super().__init__(config, objectconfig, storage)
        Thread.__init__(self)

    def get_channels(self):
        return list()

    def run(self):
        permit = self.get_config("permit", "sources")
        addr = self.get_config("address", "/get")
        port = self.get_config("port", 8000)

        if permit == "sources":
            try:
                channels = self.get_config("source", None)
            except KeyError:
                logging.critical("REST needs configuration for \"source\" or \"permit: all\" statement")
                return
        elif permit == "all":
            channels = None

        if not channels:
            logging.warning("no REST sources defined - allowing subscription for all channels")

        getter = Getter(self.storage)
        getter.start()

        # start websockets
        application = Application([
            (addr, RESTHandler, dict(config=self.config, getter=getter)),
        ], debug=True)
        application.listen(port)

        IOLoop.instance().start()

    def cancel(self):
        # TODO
        pass
