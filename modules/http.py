import logging
import requests

from .base.sources import TimedSource



class HTTPGet(TimedSource):
    def poll(self):
        url = self.get_config("url")
        try:
            out = requests.get(url).text
            value = self.typecast(out.strip())
            self.push(value)
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in HTTPGet for \"" + url + "\""
            ]))
