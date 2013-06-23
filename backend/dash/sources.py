import netsnmp
from time import time

from data import Source


class SNMP(Source):

    original_source = True

    def __init__(self, host, oids, port=None, version=None, community=None):
        self.host = host
        self.names = oids.keys()
        self.oids = netsnmp.VarList(*[netsnmp.Varbind(oid) for oid in oids.values()])
        self.port = port or 161
        self.version = version or 1
        self.community = community or "public"

    def configure(self, data, defaults, interval):
        self.data = data
        if "snmp port" in defaults:
            self.port = defaults["snmp port"]
        if "snmp version" in defaults:
            self.version = defaults["snmp version"]
            if type(self.version) != int:
                print("WARNING: SNMP protocol version is not an integer value")
        if "snmp community" in defaults:
            self.community = defaults["snmp community"]

    def run(self):
        try:
            self._run()
        except Exception as e:
            print(type(e).__name__ + " in SNMP data source \"" + self.host + "\"")
            print(e)

    def _run(self):
        session = netsnmp.Session(DestHost=self.host,
                Version=self.version,
                RemotePort=self.port,
                Timeout=400000,
                Retries=5,
        Community=self.community)
        values = session.get(self.oids) # oid --> value
        for i in range(len(self.names)):
            self.data.add(self.names[i], values[i])



class Timestamp(Source):

    original_source = True

    """ great for debugging """
    def __init__(self, name):
        self.name = name

    def run(self):
        self.data.add(self.name, int(time()))




class HTTP(Source):

    original_source = True

    def __init__(self, name, url):
        super(HTTP, self).__init__(data)
        self.name = name
        self.url = url

    def run(self):
        try:
            self._run()
        except Exception as e:
            print(type(e).__name__ + " in HTTP data source \"" + self.url + "\"")
            print(e)

    def _run(self):
        f = urlopen(self.url)
        output = f.read().strip()
        f.close()
        self.data.add(self.name, output)
 
