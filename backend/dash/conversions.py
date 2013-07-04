from data import Source



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
                # FIXME
                b = a # no, really. FIXME.
            total += (b - a)
        bitrate = (total * 8) / self.interval
        self.data.add(self.name, bitrate)

