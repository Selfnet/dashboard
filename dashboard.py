import logging

import sources
import config
from listener import Listener
from websockets import WebHandler, WSHandler

from tornado.web import Application
from tornado.ioloop import IOLoop



class SourceThreads(object):
    def __init__(self, config):
        self.config = config
        self.active_sources = []

    def _initialize(self):
        for sourceconfig in self.config["sources"]:
            for classname, args in sourceconfig.items():
                # should usually be just one
                try:
                    c = getattr(sources, classname)
                    instance = c(self.config, args)
                    self.active_sources.append(instance)
                except ValueError as e:
                    logging.exception(" ".join([
                            type(e).__name__ + ":",
                            str(e)
                        ]))
                    for key, value in args.items():
                        logging.warning("   %s: %s" % (key, value))

    def get_channels(self):
        channels = {}
        for source in self.active_sources:
            channels[source] = source.get_channels()
        return channels

    def start(self):
        self._initialize()
        for t in self.active_sources:
            t.start()
        print(str(len(self.active_sources)) + " threads running")

if __name__ == '__main__':
    # get the configuration
    conf = config.parse_config()

    # if no sources are configured, don't even try to start threads
    if "sources" in conf:
        threads = SourceThreads(config=conf)
        threads.start()
    else:
        logging.error("no sources are configured")

    db_config = conf.get("database", {})
    channels = threads.get_channels()
    listener = Listener(db_config, channels)

    # start websockets
    application = Application([
        (r'/websocket', WSHandler, dict(config=conf, listener=listener)),
        (r'/', WebHandler),
    ], debug=True)
    application.listen(5000)

    IOLoop.instance().start()
    # TODO: two sigints are needed to terminate, fix that
