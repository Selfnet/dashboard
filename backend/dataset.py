from os import popen
from urllib import urlopen



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
        counterToRate:
            Set this to True if you add data from a counter and need the rate.
        unit:
            Unit of the values. Has no influence on how data is processed.
        factor:
            Multiply each added value with factor (i.e., 8 for bytes -> bits).
    """
    def __init__(self, length, unit=""):
        self.history = []
        self.unit = unit
        self.length = length

    def add(self, data):
        """
        Use this method to add data to the dataset. Handling of counterToRate
        values and multiplying the factor will be done here.
        Returns the value as it was added (the rate for counterToRate datasets).
        """
        self.history.append(data)
        if len(self.history) > (self.length):
            self.history.pop(0)
        return data

    def values(self):
        """
        returns a list of all stored values
        """
        return self.history

    def get(self, i=-1):
        """
        returns an item from stored values
        default: last item in list
        """
        return self.history[i]

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
    def __init__(self, host, oid, length, unit="", factor=1):
        super(SimpleSNMP, self).__init__(length, unit=unit)
        self.host = host
        self.oid = oid

    def getsnmp(self):
        """
        fetch a value from the SNMP target
        returns an integer or None
        """
        try:
            cmd = " ".join(["snmpget -c public -v 2c", self.host, self.oid])
            out = popen(cmd).readline()
            data = out.split(" ")[-1].strip()
            if not data:
                return 0
            return int(data)
        except ValueError:
            print("ERROR: can't convert " + repr(data) + " to integer")
            print("       SNMP response: " + str(out))
            print("       host: " + self.host)
            print("       SNMP OID: " + self.oid)
            return 0
        except Exception, e:
            print("ERROR: " + str(e))
            print("       host: " + self.host)
            print("       SNMP OID: " + self.oid)
            return 0

    def update(self):
        value = self.getsnmp()
        latest = self.add(value)
        return latest



class SimpleHTTP(Dataset):
    """
    Fetch an object via HTTP that contains a value.

    Uses urllib.urlopen to retrieve the object. The downloaded object should
    contain only the value and whitespaces.
    """
    def __init__(self, url, length, unit="", factor=1):
        super(SimpleHTTP, self).__init__(length, unit=unit)
        self.url = url

    def gethttp(self):
        try:
            f = urlopen(self.url)
            output = f.read().strip()
            i = int(output)
            f.close()
            return i
        except ValueError:
            print("ERROR: cannot convert HTTP response to integer")
            print("       URL: " + str(self.url))
            return 0
        except Exception, e:
            print("ERROR: " + str(e))
            print("       URL: " + str(self.url))
            return 0

    def update(self):
        value = self.gethttp()
        latest = self.add(value)
        return latest


class OctetsToBps(Dataset):
    """
    Encapsulate another dataset, poll it's values (transmitted octets) and convert them to Bps
    """
    def __init__(self, dataset, length, interval, unit="bits per second"):
        super(OctetsToBps, self).__init__(length=length, unit=unit)
        self.dataset = dataset
        self.interval = interval

    def update(self):
        try:
            latest = self.dataset.get(-1)
            secondlatest = self.dataset.get(-2)
        except IndexError:
            # happens after program start
            self.add(0)
            return 0

        # overflow check/correction
        if latest < secondlatest:
            # TODO implement counter size detection on SNMP and ask dataset for the number of bits
            bits = len(bin(secondlatest)) -2
            diff = 2**bits - secondlatest
            octetsdiff = latest + diff
        else:
            octetsdiff = latest - secondlatest

        bps = int(round(float(octetsdiff*8)/self.interval))
        self.add(bps)
        return bps


class Add(Dataset):
    """
    Collect values from multiple datasets and add them
    """
    def __init__(self, sets, length, unit=""):
        super(Add, self).__init__(length=length, unit=unit)
        self.sets = sets

    def update(self):
        total = 0
        for s in self.sets:
            total += s.get()
        self.add(total)
        return total

