import logging

from .base import PubSubSource



class Factor(PubSubSource):
    def update(self):
        timestamp, value = self.pull(name=self.get_config("source"))[0]
        if not value:
            return
        factor = self.get_config("factor")
        value = float(value) * float(factor)
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
        try:
            for source in self.get_config("source"):
                timestamp, value = self.pull(name=source)[0]
                total += float(value)
            self.push(total)
        except Exception as e:
            logging.error(" ".join([
                type(e).__name__ + ":",
                str(e),
                "in Sum for \"" + self.get_config("name") + "\""
            ]))
