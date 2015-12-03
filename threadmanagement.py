#! /usr/bin/env python3
import logging
import modules



class SourceThreads(object):
    def __init__(self, config):
        self.config = config
        self.active_sources = []

    def _initialize(self):
        for sourceconfig in self.config["sources"]:
            for classname, args in sourceconfig.items():
                # should usually be just one
                try:
                    c = getattr(modules, classname)
                    instance = c(self.config, args)
                    self.active_sources.append(instance)
                except ValueError as e:
                    logging.exception(" ".join([
                            type(e).__name__ + ":",
                            str(e)
                        ]))
                    for key, value in args.items():
                        logging.warning("   %s: %s" % (key, value))

    def get_channels(self):
        channels = {}
        for source in self.active_sources:
            channels[source] = source.get_channels()
        return channels

    def start(self):
        self._initialize()
        for t in self.active_sources:
            t.start()
        # TODO logging
        print(str(len(self.active_sources)) + " threads running")
