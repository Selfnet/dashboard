import logging
import subprocess
import netsnmp
from os import popen
from urllib2 import urlopen
from time import time
import socket

from data import Source


class SNMP(Source):

    dependencies = []

    def __init__(self, host, oids, port=None, version=None, community=None):
        self.host = host
        # due to the unique way netsnmp works we need three lists
        if type(oids) == dict:
            self.names = oids.keys()
            strings = [t[0] for t in oids.values()]
            self.func = [t[1] for t in oids.values()]
            self.oids = netsnmp.VarList(*strings)
        elif type(oids) == tuple:
            self.names = []
            strings = []
            self.func = []
            for t in oids:
                self.names.append(t[0])
                strings.append(t[1])
                self.func.append(t[2])
                self.oids = netsnmp.VarList(*strings)
        self.port = port
        self.version = version
        self.community = community

    def setup_datasets(self, data):
        self.data = data
        for name in self.names:
            self.data.add_set(name)

    def setup_defaults(self, defaults):
        if "snmp port" in defaults and not self.port:
            self.port = defaults["snmp port"]
        if "snmp version" in defaults and not self.version:
            self.version = defaults["snmp version"]
            if type(self.version) != int:
                logging.warning("SNMP protocol version is not an integer value. using version 1.")
                self.version = 1
        if "snmp community" in defaults and not self.community:
            self.community = defaults["snmp community"]

    def run(self):
        try:
            session = netsnmp.Session(DestHost=self.host,
                Version=self.version,
                RemotePort=self.port,
                Timeout=2000000,
                Retries=1,
                Community=self.community)
        except Exception as e:
            logging.error(type(e).__name__ + ": " + str(e) + " could not open SNMP session with \"" + self.host + "\"")

        try:
            values = session.get(self.oids) # oid --> value
        except Exception as e:
            logging.error(type(e).__name__ + ": " + str(e) + " while fetching SNMP data from \"" + self.host + "\"")

        if values:
            for i in range(len(self.names)):
                value = self.func[i](values[i]) if values[i] else None
                self.data.add(self.names[i], value)
        else:
            for i in range(len(self.names)):
                self.data.add(self.names[i], None)



class SNMPWalkSum(Source):
    """ do snmpwalk and add up all the results """

    dependencies = []

    def __init__(self, name, host, oid, port=None, version=None, community=None):
        self.name = name
        self.host = host
        self.oid = oid
        self.port = port or 161
        # self.version = version or 1
        self.version = "2c"
        self.community = community or "public"

    def setup_defaults(self, defaults):
        if "snmp port" in defaults:
            self.port = defaults["snmp port"]
        # if "snmp version" in defaults:
        #     self.version = defaults["snmp version"]
        #     if type(self.version) != int:
        #         logging.warning("SNMP protocol version is not an integer value")
        if "snmp community" in defaults:
            self.community = defaults["snmp community"]

    def run(self):
        var = netsnmp.VarList(netsnmp.Varbind(self.oid))

        # try:
        #     session = netsnmp.Session(DestHost=self.host,
        #         Version=self.version,
        #         RemotePort=self.port,
        #         Timeout=2000000,
        #         Retries=1,
        #         Community=self.community)
        # except Exception as e:
        #     logging.error(type(e).__name__ + ": " + str(e) + " could not open SNMP session with \"" + self.host + "\"")
        #     raise

        # try:
        #     values = session.walk(var)
        # except Exception as e:
        #     logging.error(type(e).__name__ + ": " + str(e) + " in SNMP-Walk at \"" + self.host + "\"")

        total = 0

        try:
            args = ["snmpbulkwalk", "-O", "q", "-v", str(self.version), "-c", str(self.community), str(self.host), str(self.oid)]
            process = subprocess.Popen(args, stdout=subprocess.PIPE)
            out, err = process.communicate()
            if out:
                for line in out.split(b"\n"):
                    if line:
                        value = int(line.split(" ")[1])
                        total += value
                self.data.add(self.name, total)
            else:
                self.data.add(self.name, None)
        except Exception, e:
            logging.error(type(e).__name__ + ": " + str(e) + " in SNMP-Walk at \"" + self.host + "\"")
            self.data.add(self.name, None)



class Timestamp(Source):
    """ great for debugging """
    def run(self):
        self.data.add(self.name, int(time()))




class HTTP(Source):

    dependencies = []

    def __init__(self, name, url, func=str):
        self.name = name
        self.url = url
        self.func = func

    def run(self):
        value = None
        try:
            f = urlopen(self.url, timeout=5)
            output = f.read().strip()
            f.close()
            value = self.func(output)
        except Exception as e:
            logging.error(type(e).__name__ + ": " + str(e) + " in HTTP data source \"" + self.url + "\"")
            output = None
        self.data.add(self.name, value)
 



class Subprocess(Source):

    dependencies = []

    def __init__(self, name, cmd, func=None):
        self.name = name
        self.cmd = cmd
        self.func = func

    def run(self):
        output = None
        try:
            output = popen(self.cmd).readlines()
        except Exception, e:
            logging.error(type(e).__name__ + ": " + str(e) + " in Subprocess \"" + self.cmd + "\"")
            value = None

        try:
            value = self.func(output) if self.func else output
        except Exception, e:
            logging.error(type(e).__name__ + ": " + str(e) + " while applying the output modifier in Subprocess data source")
            logging.debug("received data was: " + repr(output))
            value = None

        self.data.add(self.name, value)


class Munin(Source):
    """ asks munin nodes for stuff """

    def __init__(self, name, host, identifier, key, port=4949):
        self.name = name
        self.host = host
        self.identifier = identifier
        self.key = key
        self.port = port

    def setup_defaults(self, defaults):
        self.timeout = defaults["munin timeout"] if "munin timeout" in defaults else 1

    def get_value(self, key, output):
        for line in output.split("\n"):
            if line.startswith(key + ".value "):
                return int(line.split(" ")[1])

    def run(self):
        try:
            s = socket.create_connection((self.host, self.port), self.timeout)
            s.settimeout(self.timeout)
            cmd = "fetch " + self.identifier + "\nquit"
            s.send(cmd)
            output = ""
            while True:
                output += s.recv(2048)
                if output.endswith("\n.\n"):
                    break
            value = self.get_value(self.key, output)
        except Exception as e:
            logging.error(type(e).__name__ + ": " + str(e) + " in HTTP data source \"" + self.identifier + "\" on host \"" + self.host + "\"")
            value = None

        self.data.add(self.name, value)

class Ping(Source):
    """ round-trip time to hosts """

    def __init__(self, name, target, cmd="ping -i 0.2 -c 3 -W 1"):
        self.name = name
        self.target = target
        self.cmd = cmd

    def run(self):
        try:
            ping = popen("".join([self.cmd, " ", self.target])).readlines()
            lastline = ping[-1]
            if lastline.startswith("rtt min/avg/max/mdev = "):
                rtt = float(lastline.split("/")[4])
            else:
                logging.debug("last line of ping did not contain timings: " + repr(lastline))
                rtt = None
        except Exception as e:
            logging.error(type(e).__name__ + ": " + str(e) + " in \"" + self.cmd + " " + self.target + "\"")
            rtt = None

        self.data.add(self.name, rtt)

class Ping6(Ping):
    """ round-trip time to hosts """

    def __init__(self, name, target, cmd="ping6 -i 0.2 -c 3 -W 1"):
        self.name = name
        self.target = target
        self.cmd = cmd

