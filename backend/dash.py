#!/usr/bin/python

import json
import time
import sys
import memcache
# configuration
import config
import dataset

if __name__ == "__main__":

    meta = {}
    meta["started"] = time.time()
    meta["interval"] = config.config["interval"]

    data = {}
    for setname in config.datasets:
        d = config.datasets[setname]
        if d["type"] == "snmp":
            if len(d["targets"]) == 1:
                target = d["targets"][0]
                data[setname] = dataset.SimpleSNMP(host=target["host"], oid=target["oid"], cumulative=target["cumulative"], unit=d["unit"], factor=target["factor"])
            else:
                data[setname] = dataset.MultiSNMP(targets=d["targets"], unit=d["unit"])
    mc = memcache.Client(config.config["memcache_servers"], debug=0)

    while True:
        for d in data.values():
            d.update()
        meta["refresh"] = int(time.time())
        history = {}
        latest = {}
        for name in data:
            history[name] = data[name].getdict()
            latest[name] = {"value": data[name].getlatest()}
        
        mc.set_multi({"meta": meta, "charts": config.charts, "latest": latest, "history": history})
        time.sleep(config.config["interval"])
