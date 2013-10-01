from data import Source


class OctetsToBitrate(Source):
    def __init__(self, name, sources):
        self.name = name
        self.dependencies = sources

    def set_interval(self, interval):
        self.interval = interval

    def run(self):
        total = 0
        for name in self.dependencies:
            dataset = self.data.get_dataset(name)
            try:
                a,b = dataset.two_latest_values()
            except IndexError:
                a = 0
                b = 0

            # make sure the octets are already integers
            a = int(a)
            b = int(b)

            # this happens on the first run
            if a == 0 or b == 0:
                return

            # difference between oldest two entries, modulo 16/32/64 (overflows)
            if b < a:
                # overflow happened
                # guess the size of the counter
                size = len(bin(a) - 2)
                # round to the next multiple of 8
                size = (size + 7) / 8 * 8
                # rest to maxint(size)
                rest = 2**size - a
                a = 0
                total = rest + b
            else:
                total += (b - a)
        bitrate = (total * 8) / self.interval
        self.data.add(self.name, bitrate)


class SimpleConversion(Source):
    def __init__(self, name, source, func):
        self.name = name
        self.source = source
        self.dependencies = [source]
        self.func = func

    def run(self):
        dataset = self.data.get_dataset(self.source)
        try:
            value = dataset.latest_value()
        except IndexError:
            return
        new = self.func(value)
        self.data.add(self.name, new)




class Percentage(Source):
    def __init__(self, name, value, maximum):
        self.name = name
        self.value = value
        self.maximum = maximum
        self.dependencies = [value]

    def run(self):
        val_dataset = self.data.get_dataset(self.value)
        max_dataset = self.data.get_dataset(self.maximum)
        try:
            new = round(100.0 / max_dataset.latest_value() * val_dataset.latest_value(), 2)
        except IndexError:
            return
        except ZeroDivisionError:
            return
        self.data.add(self.name, new)




class PerSecond(Source):
    def __init__(self, name, sources):
        self.name = name
        self.dependencies = sources

    def set_interval(self, interval):
        self.interval = interval

    def run(self):
        total = 0
        for name in self.dependencies:
            dataset = self.data.get_dataset(name)
            try:
                a,b = dataset.two_latest_values()
            except IndexError:
                a = 0
                b = 0

            # make sure the octets are already integers
            a = int(a)
            b = int(b)

            # this happens on the first run
            if a == 0 or b == 0:
                return

            # difference between oldest two entries, modulo 16/32/64 (overflows)
            if b < a:
                # overflow happened
                # FIXME
                b = a # no, really. FIXME.
            total += (b - a)
        rate = total / self.interval
        self.data.add(self.name, rate)

class Sum(Source):
    def __init__(self, name, sources):
        self.name = name
        self.dependencies = sources

    def run(self):
        total = 0
        for name in self.dependencies:
            dataset = self.data.get_dataset(name)
            l = int(dataset.latest_value())
            total += l
        self.data.add(self.name, total)

