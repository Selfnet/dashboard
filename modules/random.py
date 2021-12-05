import logging
import random

from .base.sources import TimedSource


class Random(TimedSource):

    async def poll(self):
        minimum = self.get_config("min", 0)
        maximum = self.get_config("max", 1)
        value = minimum + (random.random() * (maximum - minimum))
        await self.push(value)
