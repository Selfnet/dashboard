#! /usr/bin/env python3
import logging
import modules


class WorkerThreads(object):
    def __init__(self, config):
        self.config = config
        self.active_workers = []

    def _initialize(self):
        for workerconfig in self.config["workers"]:
            for classname, args in workerconfig.items():
                # should usually be just one
                try:
                    c = getattr(modules, classname)
                    instance = c(self.config, args)
                    self.active_workers.append(instance)
                except ValueError as e:
                    logging.exception(" ".join([
                            type(e).__name__ + ":",
                            str(e)
                        ]))
                    for key, value in args.items():
                        logging.warning("   %s: %s" % (key, value))

    def get_channels(self):
        channels = {}
        for worker in self.active_workers:
            channels[worker] = worker.get_channels()
        return channels

    def start(self):
        self._initialize()
        for t in self.active_workers:
            t.start()
        # TODO logging
        logging.info(str(len(self.active_workers)) + " workers running")
