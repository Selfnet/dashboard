#!/usr/bin/python

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--loglevel", type=str, metavar="LEVEL", choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"], help="CRITICAL, ERROR, WARNING, INFO (default) or DEBUG", default="INFO")
parser.add_argument("--logfile", type=str, metavar="PATH", help="path and filename for the logfile")
parser.add_argument("--test", action="store_true", help="don't write any data to memcache")
args = parser.parse_args()

import logging
loglevel = {"CRITICAL": logging.CRITICAL, "ERROR": logging.ERROR, "WARNING": logging.WARNING, "INFO": logging.INFO, "DEBUG": logging.DEBUG}[args.loglevel]

log = logging.getLogger()
formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

ch = logging.StreamHandler()
log.addHandler(ch)
log.setLevel(loglevel)
ch.setFormatter(formatter)

if args.logfile:
    fh = logging.FileHandler(args.logfile)
    fh.setFormatter(formatter)
    log.addHandler(fh)

log.info("dashboard started")

if args.test:
    logging.warning("test mode - output data will not be stored in memcache!")

log.debug("loading modules")
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
                log.debug("executing %s", path)
                exec(compile(open(path).read(), path, 'exec'), globals(), locals())
        else:
            execute_files(path)

def update_loop():
    timer = Timer(conf.interval, update_loop).start()

    log.debug("update: fetching data")

    # fetch raw data from all the sources
    t1 = time.time()
    pool.map(lambda x: x(), independent_jobs)

    log.debug("update: deriving datasets")

    # process data
    for job in meta_jobs:
        job()

    t2 = time.time()

    if not args.test:
        logging.debug("update: writing outputs")
        pool.map(lambda x: x(), outputs)

    log.info("update done, {0:.2f} seconds".format(t2-t1))


# load config
conf = Config()
execute_files("conf.d")
independent_jobs = conf.get_independent_callables()
meta_jobs = conf.get_meta_callables()
outputs = conf.get_output_callables()

# execute jobs
pool = ThreadPool(processes=8)

update_loop()

