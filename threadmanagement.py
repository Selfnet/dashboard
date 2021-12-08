#! /usr/bin/env python3
import logging
import modules
import asyncio


class WorkerThreads(object):
    def __init__(self, config, storage):
        self.config = config
        self.storage = storage
        self.active_workers = []

    def get_channels(self):
        channels = {}
        for worker in self.active_workers:
            channels[worker] = worker.get_channels()
        return channels

    def _initialize(self):
        for workerconfig in self.config["workers"]:
            for classname, args in workerconfig.items():
                # should usually be just one
                try:
                    c = getattr(modules, classname)
                    instance = c(self.config, args, self.storage)
                    self.active_workers.append(instance)
                except ValueError as e:
                    logging.exception(" ".join([
                        type(e).__name__ + ":",
                        str(e)
                    ]))
                    for key, value in args.items():
                        logging.warning("   %s: %s" % (key, value))

    def _prepare(self):
        logging.info('Starting preparation')
        for t in self.active_workers:
            t.prepare()
        logging.info('Preparation done')

    async def _start(self):
        logging.info('Starting storage')
        asyncio.create_task(self.storage.start())
        logging.info('Creating tasks')
        for t in self.active_workers:
            asyncio.create_task(t.start())
        logging.info('Task creation done')

    def start(self):
        self._initialize()
        self._prepare()
        logging.info(str(len(self.active_workers)) + " workers prepared and will be started")
        logging.info('Starting event loop')
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._start())
        loop.run_forever()
