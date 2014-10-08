import os
import time
import logging

import config
import sources



conf = config.parse_config()


# spawn threads for sources
active_sources = []

if "sources" not in conf:
    raise Exception("no sources configured")

for args in conf["sources"]:
    try:
        c = getattr(sources, args["class"])
        instance = c(conf, args)
        active_sources.append(instance)
    except ValueError as e:
        logging.error(" ".join([
                type(e).__name__ + ":",
                str(e)
            ]))
        for key, value in args.items():
            logging.warning("   %s: %s" % (key, value))


# start threads
for t in active_sources:
    t.start()
print(str(len(active_sources)) + " threads running")
