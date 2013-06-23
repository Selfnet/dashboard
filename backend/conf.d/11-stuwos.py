from dash.sources import SNMP

# BORDER ROUTER TRAFFIC
conf.add(SNMP(
    host="stuwost1",
    oids={
        "octets stuwost1 to belwue": ".1.3.6.1.2.1.31.1.1.1.10.570",
        "octets stuwost1 to belwue ipv6": ".1.3.6.1.4.1.2636.3.11.1.3.1.1.2.570",
        "octets belwue to stuwost1": ".1.3.6.1.2.1.31.1.1.1.6.570",
        "octets belwue to stuwost1 ipv6": ".1.3.6.1.4.1.2636.3.11.1.3.1.1.1.570",
        "routes ipv4 stuwost1": "iso.3.6.1.4.1.2636.5.1.1.2.6.2.1.8.0.1.1",
        "routes ipv6 stuwost1": "iso.3.6.1.4.1.2636.5.1.1.2.6.2.1.8.1.2.1"
    }
))
