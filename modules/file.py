import logging
from aiofile import async_open
from .base.sources import TimedSource


class File(TimedSource):

    async def poll(self):
        filename = self.get_config("filename")
        strip = self.get_config("strip", True)
        try:
            async with async_open(filename, "r") as f:
                content = await f.read()
                if isinstance(content, bytes):
                    content = content.decode("utf-8")
                if strip:
                    content = content.strip()
                await self.push(content)
        except FileNotFoundError:
            logging.info("File \"{name}\" not found".format(name=filename))
