#!/usr/bin/python

import json
import time
import sys
import memcache

import config


if __name__ == "__main__":

    meta = {}
    meta["started"] = time.time()
    meta["interval"] = config.interval

    data = {}
    mc = memcache.Client(config.settings["memcache_servers"], debug=0)

    while True:
        for d in config.poll:
            d.update()
        meta["refresh"] = int(time.time())
        history = {}
        latest = {}
        for key in config.publish:
            dataset = config.publish[key]
            history[key] = dataset.getdict()
            latest[key] = {"value": dataset.getlatest()}
        
        mc.set_multi({"meta": meta, "latest": latest, "history": history})
        time.sleep(meta["interval"])
