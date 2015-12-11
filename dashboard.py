#! /usr/bin/env python3
import logging

import config
import storage
from threadmanagement import WorkerThreads


if __name__ == '__main__':
    # get the configuration
    conf = config.parse_config()
    stor = storage.Storage()

    # if no sources are configured, don't even try to start threads
    if "workers" in conf:
        threads = WorkerThreads(config=conf, storage=stor)
        threads.start()
    else:
        logging.critical("no workers are configured")
