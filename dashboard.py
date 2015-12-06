#! /usr/bin/env python3
import logging

import config
from threadmanagement import WorkerThreads


if __name__ == '__main__':
    # get the configuration
    conf = config.parse_config()

    # if no sources are configured, don't even try to start threads
    if "workers" in conf:
        threads = WorkerThreads(config=conf)
        threads.start()
    else:
        logging.critical("no workers are configured")
