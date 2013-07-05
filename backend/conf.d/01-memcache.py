from dash.output import Memcache

conf.output(Memcache(["localhost:11211"], conf))

