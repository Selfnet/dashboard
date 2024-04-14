from .base.sources import PubSubSource


class Printer(PubSubSource):

    async def update(self, item):
        for name in self.get_config("source"):
            last_ts, last_val = await self.pull(name)[0]
            print(last_ts + b" " + last_val)
