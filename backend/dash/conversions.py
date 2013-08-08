from data import Source


def latest_value(l):
    a = None
    i = 1
    while a == None:
        a = l[-i]
        i += 1
    return a

def two_latest_values(l):
    # find the two most recent values != None
    a = None # first value
    b = None # second (most recent) value
    i = 1
    while b == None:
        b = l[-i]
        i += 1
    # found b
    while a == None:
        a = l[-i]
        i += 1 
    # found a
    return a,b


class OctetsToBitrate(Source):
    def __init__(self, name, sources):
        self.name = name
        self.dependencies = sources

    def configure(self, data, defaults, interval):
        self.data = data
        self.data.add_set(self.name)
        self.interval = interval

    def run(self):
        total = 0
        for name in self.dependencies:
            dataset = self.data.get_dataset(name)
            try:
                a,b = two_latest_values(dataset)
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
            value = latest_value(dataset)
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
            new = 100.0 / latest_value(max_dataset) * latest_value(val_dataset)
        except IndexError:
            return
        self.data.add(self.name, new)




class PerSecond(Source):
    def __init__(self, name, sources):
        self.name = name
        self.dependencies = sources

    def configure(self, data, defaults, interval):
        self.data = data
        self.data.add_set(self.name)
        self.interval = interval

    def run(self):
        total = 0
        for name in self.dependencies:
            dataset = self.data.get_dataset(name)
            try:
                a,b = two_latest_values(dataset)
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
            l = int(latest_value(dataset))
            total += l
        self.data.add(self.name, total)

