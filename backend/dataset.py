from os import popen
from config import config


def rate(value, interval):
    return int(round(float(value)/interval));


class Dataset(object):
    def __init__(self, cumulative=False, unit="", factor=1):
        self.history = []
        self.lastvalue = 0
        self.cumulative = cumulative
        self.unit = unit
        self.factor = factor
        self.interval = config["interval"]
        self.maxvalues = config["maxvalues"]

    def add(self, data):
        data = data * self.factor
        if self.cumulative:
            if self.lastvalue == 0:
                self.lastvalue = data
                return 0
            if data < self.lastvalue:
                # counter overflow
                bits = len(bin(self.lastvalue)) -2
                diff = 2**bits - self.lastvalue
                value = rate(data + diff, self.interval)
            else:
                value = rate(data - self.lastvalue, self.interval)
        else:
            value = data

        if self.maxvalues:
            self.history.append(value)
            if len(self.history) > (self.maxvalues):
                self.history.pop(0)
        self.lastvalue = data
        return value

    def values(self):
        return self.history

    def getdict(self):
        return {"unit": self.unit, "values": self.values()}

    def getlatest(self):
        try:
            return self.history[-1]
        except IndexError:
            return

    def __str__(self):
        return repr(self.values())


class SimpleSNMP(Dataset):
    def __init__(self, host, oid, cumulative=False, unit="", factor=1):
        super(SimpleSNMP, self).__init__(cumulative=cumulative, unit=unit, factor=factor)
        self.host = host
        self.oid = oid

    def getsnmp(self):
        cmd = " ".join(["snmpget -c public -v 2c", self.host, self.oid])
        out = popen(cmd).readline()
        data = out.split(" ")[-1].strip()
        if not data:
            return
        try:
            return int(data)
        except ValueError:
            print("ERROR: can't convert " + repr(data) + " to integer")
            print("       response: " + str(out))
            print("       host: " + host)
            print("       oid: " + oid)
            return

    def update(self):
        value = self.getsnmp()
        latest = self.add(value)
        return latest


class MultiSNMP(Dataset):
    def __init__(self, targets={}, unit="", factor=1):
        super(MultiSNMP, self).__init__(cumulative=False, unit=unit)
        self.targets = []
        for t in targets:
            s = SimpleSNMP(host=t["host"], oid=t["oid"], cumulative=t["cumulative"], factor=t["factor"])
            s.maxvalues = 0
            self.targets.append(s)
    
    def update(self):
        total = 0
        for t in self.targets:
            total += t.update()
        self.add(total)

