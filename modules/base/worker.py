import logging


class Worker():

    def __init__(self, config, objectconfig, storage):
        # settings and parameters
        self.config = config
        self.objectconfig = objectconfig
        self.storage = storage

    def prepare(self):
        """
        gets called after all sources have been created, and before
        threads are started
        """
        pass

    def get_config(self, key, default=None):
        # priority 1: value is configured for this object
        try:
            value = self.objectconfig[key]
            return value
        except KeyError:
            # try again
            pass

        # priority 2: as class default
        try:
            # try to find the key in the defaults for this object type
            value = self.config["defaults"][self.__class__.__name__][key]
            return value
        except KeyError:
            # still nope
            pass

        # priority 3: value is configured as global default
        try:
            value = self.config["defaults"][key]
            return value
        except KeyError:
            # and again
            pass

        # still no luck? has something been set as hard-coded default?
        if default != None:
            return default

        # last measure
        raise KeyError("config parameter \"{key}\" not configured for {classname}".format(key=key, classname=self.__class__.__name__))
