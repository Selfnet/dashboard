import logging
from os import popen

# BORDER ROUTER TRAFFIC

# dirty hack: call snmpwalk to get the right interface-ID

output = popen("snmpbulkwalk -c public -v 2c stuwost1 .1.3.6.1.2.1.31.1.1.1 | grep AS553").readline()
stuwost1uplink = output.split(" =")[0].split(".")[-1]

logging.info("stuwost1 uplink interface id: " + str(stuwost1uplink))

conf.add(SNMP(
    host="stuwost1",
    oids={
        "octets stuwost1 to belwue": "iso.3.6.1.2.1.31.1.1.1.10." + stuwost1uplink,
        "octets stuwost1 to belwue ipv6": "iso.3.6.1.4.1.2636.3.11.1.3.1.1.2." + stuwost1uplink,
        "octets belwue to stuwost1": "iso.3.6.1.2.1.31.1.1.1.6." + stuwost1uplink,
        "octets belwue to stuwost1 ipv6": "iso.3.6.1.4.1.2636.3.11.1.3.1.1.1." + stuwost1uplink,
        "routes ipv4 stuwost1 raw": "iso.3.6.1.4.1.2636.5.1.1.2.6.2.1.8.0.1.1",
        "routes ipv6 stuwost1 raw": "iso.3.6.1.4.1.2636.5.1.1.2.6.2.1.8.1.2.1"
    }
))



output = popen("snmpbulkwalk -c public -v 2c stuwost2 .1.3.6.1.2.1.31.1.1.1 | grep AS553").readline()
stuwost2uplink = output.split(" =")[0].split(".")[-1]

logging.info("stuwost2 uplink interface id: " + str(stuwost2uplink))

conf.add(SNMP(
    host="stuwost2",
    oids={
        "octets stuwost2 to belwue": "iso.3.6.1.2.1.31.1.1.1.10." + stuwost2uplink,
        "octets stuwost2 to belwue ipv6": "iso.3.6.1.4.1.2636.3.11.1.3.1.1.2." + stuwost2uplink,
        "octets belwue to stuwost2": "iso.3.6.1.2.1.31.1.1.1.6." + stuwost2uplink,
        "octets belwue to stuwost2 ipv6": "iso.3.6.1.4.1.2636.3.11.1.3.1.1.1." + stuwost2uplink,
        "routes ipv4 stuwost2 raw": "iso.3.6.1.4.1.2636.5.1.1.2.6.2.1.8.0.1.1",
        "routes ipv6 stuwost2 raw": "iso.3.6.1.4.1.2636.5.1.1.2.6.2.1.8.1.2.1"
    }
))

# convert routes to integer
conf.add(SimpleConversion(name="routes ipv4 stuwost1", source="routes ipv4 stuwost1 raw", func=int))
conf.add(SimpleConversion(name="routes ipv6 stuwost1", source="routes ipv6 stuwost1 raw", func=int))
conf.add(SimpleConversion(name="routes ipv4 stuwost2", source="routes ipv4 stuwost2 raw", func=int))
conf.add(SimpleConversion(name="routes ipv6 stuwost2", source="routes ipv6 stuwost2 raw", func=int))

