import logging
import json
import time
from aiofile import async_open

from .base.sources import TimedSource


class PersistentStorage(TimedSource):
    def prepare(self):
        filename = self.get_config("filename")
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            gap = time.time() - data["timestamp"]
            logging.info("loading PersistentStorage from file \"{filename}\" (gap: {secs} seconds)".format(filename=filename, secs=gap))
            self.storage.load(data["data"])
        except Exception as e:
            logging.info("failed to load PersistenStorage: {exception}".format(exception=str(e)))

    async def poll(self):
        datasets = await self.storage.dump()
        data = {"timestamp": time.time(), "data": datasets}
        filename = self.get_config("filename")
        async with async_open(filename, "w") as f:
            await f.write(json.dumps(data))
