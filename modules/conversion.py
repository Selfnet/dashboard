import logging

from .base import PubSubSource



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
    def update(self, triggered_by):
        timestamp, value = self.pull(name=self.get_config("source"))[0]
        if not value:
            return
        factor = self.get_config("factor")
        value = float(value) * float(factor)
        self.push(value)

class OctetsToBps(PubSubSource):
    def update(self, triggered_by):
        sources = self.get_config("source")
        if type(sources) == type(""):
            sources = [sources]
        total_bps = 0
        for source in sources:
            data = self.pull(name=source, n=2)
            try:
                timediff = float(data[0][0]) - float(data[1][0])
                counterdiff = counter_difference(int(data[0][1]), int(data[1][1]))
                bps = (counterdiff / timediff) * 8
            except IndexError:
                # not enough data
                if len(sources) == 1:
                    return
                else:
                    bps = 0
            total_bps += bps
        self.push(total_bps)

class Sum(PubSubSource):
    def update(self, triggered_by):
        total = 0
        try:
            for source in self.get_config("source"):
                timestamp, value = self.pull(name=source)[0]
                total += float(value)
            self.push(total)
        except Exception as e:
            logging.exception(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in Sum for \"" + self.get_config("name") + "\""
            ]))
