import logging
from data import Data
from sources import *
from conversions import *
import os



class Config():
    def __init__(self, data=None):
        # config + defaults
        self.interval = 60 # default value
        self.defaults = {}
        self.defaults["dataset size"] = 300

        # internals
        self.independent_jobs = []
        self.meta_jobs = []
        self.published_sets = []
        self.outputs = []

        if not data:
            data = Data(self)
        self.data = data

    def get_independent_callables(self):
        return [job.run for job in self.independent_jobs]

    def get_meta_callables(self):
        return [job.run for job in self.meta_jobs]

    def get_output_callables(self):
        return [job.run for job in self.outputs]

    def add(self, job):
        job.setup_datasets(self.data)
        job.setup_defaults(self.defaults)
        job.set_interval(self.interval)
        if job.dependencies:
            for dep in job.dependencies:
                if not self.data.has_set(dep):
                    logging.warning("invalid config: \"" + str(dep) + "\" must be configured before \"" + str(job.name) + "\". " + str(job.name) + " will be ignored")
                    return
            self.meta_jobs.append(job)
        else:
            self.independent_jobs.append(job)

    def output(self, o):
        self.outputs.append(o)

    def publish_list(self, l):
        for name in l:
            self.publish(name)

    def publish(self, name):
        self.published_sets.append(name)

    def get_published(self):
        return self.published_sets

