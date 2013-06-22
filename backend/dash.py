#!/usr/bin/python

import os
import sys
import time
from multiprocessing.pool import ThreadPool
from threading import Timer

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
    pool.map(lambda x: x(), fetch_jobs)

    # process datA
    pool.map(lambda x: x(), meta_jobs)




# load config
conf = Config()
execute_files("conf.d")
fetch_jobs = conf.get_fetch_jobs()
meta_jobs = conf.get_meta_jobs()

# execute jobs
pool = ThreadPool(processes=4)

update_loop()

