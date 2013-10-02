#!/usr/bin/python

import logging

import argparse
parser = argparse.ArgumentParser()

parser.add_argument(
    "--loglevel",
    type=str,
    metavar="LEVEL",
    choices=["CRITICAL",
    "ERROR", "WARNING", "INFO", "DEBUG"],
    help="CRITICAL, ERROR, WARNING, INFO (default) or DEBUG",
)
parser.add_argument(
    "--test",
    action="store_true",
    help="don't write any data to memcache"
)

args = parser.parse_args()




import os
import sys
import time
from multiprocessing.pool import ThreadPool
from threading import Timer
import memcache
from dash.config import Config




def execute_files(folder):
    items = os.listdir(folder)
    items.sort()
    for item in items:
        path = os.path.join(folder, item)
        if os.path.isfile(path):
            if path.endswith(".py"):
                exec(compile(open(path).read(), path, 'exec'), globals(), locals())
        else:
            execute_files(path)

def update_loop():
    timer = Timer(conf.interval, update_loop).start()

    logging.debug("update: fetching data")

    # fetch raw data from all the sources
    t1 = time.time()
    pool.map(lambda x: x(), independent_jobs)

    logging.debug("update: deriving datasets")

    # process data
    for job in meta_jobs:
        job()

    t2 = time.time()

    if not args.test:
        logging.debug("update: writing outputs")
        pool.map(lambda x: x(), outputs)
    else:
        logging.debug("test mode - suppressing output")

    logging.info("update done, {0:.2f} seconds".format(t2-t1))




# load config
conf = Config()
execute_files("conf.d")

if args.loglevel:
    conf.set_loglevel(args.loglevel)
    logging.info("loglevel reset by command line argument")
if args.test:
    logging.warning("test mode - output data will not be stored in memcache!")

independent_jobs = conf.get_independent_callables()
meta_jobs = conf.get_meta_callables()
outputs = conf.get_output_callables()

# execute jobs
threads = getattr(conf, "threads", None)
if not threads:
    threads = len(independent_jobs)
logging.info("starting " + str(threads) + " threads")
pool = ThreadPool(threads)

logging.debug("entering main loop")

update_loop()

