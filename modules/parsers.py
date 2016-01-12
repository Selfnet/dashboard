import logging
from operator import itemgetter
import json

from .base.sources import PubSubSource


class JSONParser(PubSubSource):
    def update(self, channel, timestamp, value):
        # get parameters
        path = self.get_config("path", [])

        # get the data
        try:
            value = json.loads(value)
        except Exception as e:
            logging.warning("Error in JSONParser: " + str(e))
            return

        # get the right element
        if path and isinstance(path, str):
            path = [path]
        if path and isinstance(path, list):
            for item in path:
                getter = itemgetter(item)
                try:
                    value = getter(value)
                except:
                    logging.info("Could not get item \"{key}\"".format(key=str(item)))
                    return

        # write the data
        self.push(value)
