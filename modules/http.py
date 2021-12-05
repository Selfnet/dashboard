import logging
import aiohttp

from .base.sources import TimedSource


class HTTPGet(TimedSource):
    async def poll(self):
        url = self.get_config("url")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    out = await resp.text()
                    value = self.typecast(out.strip())
                    await self.push(value)
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in HTTPGet for \"" + url + "\""
            ]))
