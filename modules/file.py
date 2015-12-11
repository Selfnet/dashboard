import logging

from .base.sources import TimedSource



class File(TimedSource):

    def poll(self):
        filename = self.get_config("filename")
        strip = self.get_config("strip", True)
        try:
            with open(filename, "r") as f:
                content = f.read()
                if strip:
                    content = content.strip()
                self.push(content)
        except FileNotFoundError:
            logging.info("File \"{name}\" not found".format(name=filename))
