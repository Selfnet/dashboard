import logging
from operator import itemgetter
import json
import yaml

from .base.sources import PubSubSource


class Parser(PubSubSource):

    def parse(self, data):
        pass

    def getitem(self, data, path):
        if isinstance(path, list):
            for item in path:
                getter = itemgetter(item)
                data = getter(data)
            return data
        else:
            return data[path]

    def update(self, channel, timestamp, value):
        # get parameters
        path = self.get_config("path", [])

        # get the data
        try:
            value = self.parse(value)
        except Exception as e:
            logging.warning(str(e))
            return

        # if a path is set, try to get the item
        if path:
            try:
                value = self.getitem(value, path)
            except Exception as e:
                logging.info(str(e))

        # write the data
        self.push(value)


class JSONParser(Parser):

    def parse(self, data):
        return json.loads(data)


class YAMLParser(Parser):

    def parse(self, data):
        return yaml.load(data)
