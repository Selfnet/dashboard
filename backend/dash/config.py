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
        self.fetch_jobs = []
        self.meta_jobs = []
        self.published_sets = {}

        if not data:
            data = Data(self.defaults["dataset size"])
        self.data = data


    def get_fetch_jobs(self):
        return self.fetch_jobs

    def get_meta_jobs(self):
        return self.meta_jobs

    def add(self, job):
        job.configure(self.data, self.defaults, self.interval)
        if job.original_source:
            self.fetch_jobs.append(job.run)
        else:
            self.meta_jobs.append(job.run)

    def publish_list(self, l):
        for name in l:
            self.publish(name)

    def publish(self, name):
        self.published_sets["name"] = self.data.get_dataset(name)

