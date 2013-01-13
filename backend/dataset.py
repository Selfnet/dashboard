from os import popen
from config import config
from urllib import urlopen


def rate(value, interval):
    """
    returns [unit]/sec as an integer
    """
    return int(round(float(value)/interval));


class Dataset(object):
    """
    abstract dataset object

    Implements all the basic functions needed to store and retrieve values.
    Since this is an abstract class to provide basic data handling, it does not
    implement an update()-method. Usable Datasets must implement that method.
    Subclass this to add functionality for different ways of gathering data.
    The method called to fetch a new value is update() which should pass new
    data to the add()-method.
    Parameters needed:
        cumulative:
            Set this to True if you add data from a counter and need the rate.
        unit:
            Unit of the values. Has no influence on how data is processed.
        factor:
            Multiply each added value with factor (i.e., 8 for bytes -> bits).
    """
    def __init__(self, cumulative=False, unit="", factor=1):
        self.history = []
        self.lastvalue = 0
        self.cumulative = cumulative
        self.unit = unit
        self.factor = factor
        self.interval = config["interval"]
        self.maxvalues = config["maxvalues"]

    def add(self, data):
        """
        Use this method to add data to the dataset. Handling of cumulative
        values and multiplying the factor will be done here.
        Returns the value as it was added (the rate for cumulative datasets).
        """
        try:
            data = data * self.factor
        except TypeError:
            data = 0
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
        """
        returns a list of all stored values
        """
        return self.history

    def getdict(self):
        """
        returns a dict that contains all the stored values and the unit
        """
        return {"unit": self.unit, "values": self.values()}

    def getlatest(self):
        """
        return only the latest value or None
        """
        try:
            return self.history[-1]
        except IndexError:
            return

    def __str__(self):
        return repr(self.getdict())


class SimpleSNMP(Dataset):
    """
    get data from SNMP-target

    Uses subprocess.popen to call snmpget. Returned value is the last part
    (separated by space) of the response.
    Subclasses Dataset, to inherit basic data storage behaviour.
    """
    def __init__(self, host, oid, cumulative=False, unit="", factor=1):
        super(SimpleSNMP, self).__init__(cumulative=cumulative, unit=unit, factor=factor)
        self.host = host
        self.oid = oid

    def getsnmp(self):
        """
        fetch a value from the SNMP target
        returns an integer or None
        """
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
    """
    get aggregated data from multiple SNMP-targets

    Builds a list of SimpleSNMP-objects that gather the data from every target.
    It's also a Dataset-object by itself, so it inherits methods like getdict().
    """
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


class SimpleHTTP(Dataset):
    """
    Fetch an object via HTTP that contains a value.

    Uses urllib.urlopen to retrieve the object. The downloaded object should
    contain only the value and whitespaces.
    """
    def __init__(self, url, cumulative=False, unit="", factor=1):
        super(SimpleHTTP, self).__init__(cumulative=cumulative, unit=unit, factor=factor)
        self.url = url

    def gethttp(self):
        try:
            f = urlopen(self.url)
            i = int(f.read().strip())
            f.close()
            return i
        except ValueError:
            return 0

    def update(self):
        value = self.gethttp()
        latest = self.add(value)
        return latest
        
