#!/usr/bin/python

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

    # fetch raw data from all the sources
    t1 = time.time()
    pool.map(lambda x: x(), independent_jobs)

    # process data
    for job in meta_jobs:
        job()
    t2 = time.time()

    pool.map(lambda x: x(), outputs)
    print("update done, {0:.2f}s".format(t2-t1))


# load config
conf = Config()
execute_files("conf.d")
independent_jobs = conf.get_independent_callables()
meta_jobs = conf.get_meta_callables()
outputs = conf.get_output_callables()

# execute jobs
pool = ThreadPool(processes=8)

update_loop()

