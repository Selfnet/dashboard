import os
import json



# recursively merge dictionaries
# by Andrew Cooke
# http://stackoverflow.com/questions/7204805/dictionaries-of-dictionaries-merge
# adapted to also lists as well
def merge(a, b, path=None):
    "merges b into a and raises an exception on conflicts"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif isinstance(a[key], list) and isinstance(b[key], list):
                a[key] = a[key] + b[key]
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a



def parse_config():
    "load all files in conf.d, parse and merge them"
    path = os.path.join(os.path.dirname(__file__), "conf.d")
    files = os.listdir(path)
    files.sort()

    config = {}

    for filename in files:
        configfile = os.path.join(path, filename)
        try:
            c = json.load(open(configfile, "r"))
        except ValueError as e:
            print(filename + ": " + str(e))
            print("{filename}: file ignored".format(filename=filename))
            c = {}
        merge(config, c)

    return config
