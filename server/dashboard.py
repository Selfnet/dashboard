import time
import logging

import source


# load/execute config file
configfile = "config.py"
exec(compile(open(configfile).read(), configfile, 'exec'), globals(), locals())


# set general default-settings
source.Source.settings.update(settings)

for classname, args in defaults.items():
    c = getattr(source, classname)
    c.defaults.update(args)


# spawn threads for sources
active_sources = []

for item in sources:
    classname, args = item
    try:
        c = getattr(source, classname)
        instance = c(**args)
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
