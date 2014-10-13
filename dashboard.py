import sys
import logging

import sources
import config
from websockets import WebHandler, WSHandler

from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

class SourceThreads(object):
    def __init__(self):
        self.active_sources = []

    def read_config(self):
        self.conf = config.parse_config()
        if "sources" not in self.conf:
            raise Exception("no sources configured")

    def _initialize(self):
        for sourceconfig in self.conf["sources"]:
            for classname, args in sourceconfig.items():
                # should usually be just one
                try:
                    c = getattr(sources, classname)
                    instance = c(self.conf, args)
                    self.active_sources.append(instance)
                except ValueError as e:
                    logging.exception(" ".join([
                            type(e).__name__ + ":",
                            str(e)
                        ]))
                    for key, value in args.items():
                        logging.warning("   %s: %s" % (key, value))

    def start(self):
        self._initialize()
        for t in self.active_sources:
            t.start()
        print(str(len(self.active_sources)) + " threads running")

if __name__ == '__main__':
    # threads = SourceThreads()
    # try:
    #     threads.read_config()
    # except Exception as e:
    #     logging.error(e)
    #     sys.exit(20)
    # threads.start()

    application = Application([
        (r'/websocket', WSHandler),
        (r'/', WebHandler),
    ], debug=True)
    application.listen(5000)

    IOLoop.instance().start()
    # TODO: two sigints are needed to terminate, fix that
