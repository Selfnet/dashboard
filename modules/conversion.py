import logging

from .base.sources import PubSubSource


def countersize(i):
    " estimates the size of the counter used; possible sizes are in 2**n, n>2 "
    n = 3  # start at 8 bit
    while True:
        if i.bit_length() < 2**n:
            return 2**n
        else:
            n += 1


def counter_difference(this, last):
    if this >= last:
        return this - last
    else:
        # counter overflow
        size = countersize(last)
        # difference to the full counter
        diff = 2**size - last
        # from empty counter
        diff += this
        return diff


class Factor(PubSubSource):
    async def update(self, channel, timestamp, value):
        factor = self.get_config("factor")
        value = float(value) * float(factor)
        await self.push(value)


class OctetsToBps(PubSubSource):
    async def update(self, channel, timestamp, value):
        logging.info('Converting octets to bps')
        sources = self.get_config("source")
        if isinstance(sources, str):
            sources = [sources]
        total_bps = 0
        for source in sources:
            data = await self.pull(channel=source, n=2)
            try:
                timediff = float(data[1][0]) - float(data[0][0])
                counterdiff = counter_difference(int(data[1][1]), int(data[0][1]))
                bps = (counterdiff / timediff) * 8
            except IndexError:
                logging.warning('Error in Conversion: ' + str(data))
                # not enough data
                if len(data) == 1:
                    return
                else:
                    bps = 0
            total_bps += bps
        await self.push(total_bps)


class Sum(PubSubSource):
    async def update(self, channel, timestamp, value):
        total = 0
        try:
            for source in self.get_config("source"):
                data = await self.pull(channel=source, n=1)
                total += data[0][1]
            await self.push(total)
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in Sum for \"" + self.get_config("name") + "\""
            ]))
