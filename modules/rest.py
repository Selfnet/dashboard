import logging
import time
import json
from .base.worker import Worker
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler, HTTPError, asynchronous
from tornado.gen import engine, Task
from queue import Queue
from threading import Thread, Lock, Event


class RESTHandler(RequestHandler):
    def initialize(self, **kwargs):
        self.allowed_channels = kwargs["allowed_channels"]
        self.storage = kwargs["storage"]

    @asynchronous
    @engine
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

        if self.allowed_channels:
            channels = [channel for channel in channels if channel in self.allowed_channels]

        def fetchdata(storage, channels, n, time_min, time_max, callback):
            datasets = {}
            for channel in channels:
                datasets[channel] = storage.get(channel=channel, n=n)
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
            IOLoop.instance().add_callback(lambda: callback(response))

        response = yield Task(fetchdata,
            storage=self.storage,
            channels=channels,
            n=last,
            time_min=time_min,
            time_max=time_max,
        )
        self.write(response)
        self.finish()


class REST(Worker, Thread):

    def __init__(self, config, objectconfig, storage):
        super().__init__(config, objectconfig, storage)
        Thread.__init__(self)

    def get_channels(self):
        return list()

    def prepare(self):
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

        # start websockets
        application = Application([
            (addr, RESTHandler, dict(allowed_channels=channels, storage=self.storage)),
        ], debug=False)
        application.listen(port)

    def run(self):
        ioloop = IOLoop.instance()
        logging.warning("ioloop status " + str(ioloop._running))
        if not ioloop._running:
            logging.warning("starting ioloop in REST")
            ioloop.start()

    def cancel(self):
        IOLoop.instance().stop()
