conf.add(SNMP(
    host="10.0.2.21",
    oids={
        "user vpn clients raw": "iso.3.6.1.4.1.9.9.392.1.3.3.0"
    }
))

# convert to integer
conf.add(SimpleConversion(name="user vpn clients", source="user vpn clients raw", func=int))
