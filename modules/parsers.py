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

    async def update(self, channel, timestamp, value):
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

                # write the data
                await self.push(value)

            except Exception as e:
                # Write no data, but log the error
                logging.info(str(e))


class JSONParser(Parser):

    def parse(self, data):
        return json.loads(data)


class YAMLParser(Parser):

    def parse(self, data):
        return yaml.load(data)
