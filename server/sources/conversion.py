
from .base import PubSubSource



class Factor(PubSubSource):
    def update(self):
        value = self.pull(name=self.get_config("source"))
        value = float(value) * float(self.get_config("factor"))
        self.push(value)

class OctetsToBps(PubSubSource):
    def update(self):
        sources = self.get_config("source")
        if type(sources) == type(""):
            sources = [sources]
        total_bps = 0
        for source in sources:
            data = self.pull(name=source, n=2)
            try:
                timediff = float(data[0][0]) - float(data[1][0])
                counterdiff = int(data[0][1]) - int(data[1][1])
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
    def update(self):
        total = 0
        for source in self.get_config("source"):
            total += float(self.pull(name=source))
        self.push(total)
