#! /usr/bin/env python3
import logging

import config
import threadmanagement
from listener import Listener
from websockets import WebHandler, WSHandler

from tornado.web import Application
from tornado.ioloop import IOLoop



if __name__ == '__main__':
    # get the configuration
    conf = config.parse_config()

    # if no sources are configured, don't even try to start threads
    if "sources" in conf:
        threads = threadmanagement.SourceThreads(config=conf)
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
    print("exiting main thread")
    # TODO: two sigints are needed to terminate, fix that
