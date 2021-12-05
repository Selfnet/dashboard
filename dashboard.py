#! /usr/bin/env python3
import logging
import argparse
import config
import storage
from threadmanagement import WorkerThreads


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--loglevel", metavar="LEVEL", type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Loglevel (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    args = parser.parse_args()

    if args.loglevel:
        loglevel = getattr(logging, args.loglevel.upper(), None)
        if loglevel:
            logging.basicConfig(level=loglevel)
            logging.info("set loglevel to " + str(args.loglevel))

    # get the configuration
    conf = config.parse_config()
    stor = storage.Storage()

    # if no sources are configured, don't even try to start threads
    if "workers" in conf:
        threads = WorkerThreads(config=conf, storage=stor)
        threads.start()
    else:
        logging.critical("no workers are configured")
