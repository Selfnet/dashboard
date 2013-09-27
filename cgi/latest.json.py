#!/usr/bin/python

import memcache
import json

print "Content-Type: application/json"
print

mc = memcache.Client(['127.0.0.1:11211'], debug=0)
data = mc.get_multi(["meta", "latest"])
print(json.dumps(data, separators=(",", ":")))
