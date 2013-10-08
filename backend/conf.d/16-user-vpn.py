conf.add(SNMP(
    host="10.0.2.21",
    oids={
        "user vpn clients": ("iso.3.6.1.4.1.9.9.392.1.3.3.0", int)
    }
))

