conf.add(SNMP(
    host="usv1.mgmt.selfnet.de",
    oids={
        "usv1 current raw": "iso.3.6.1.4.1.318.1.1.1.4.3.4.0",
        "usv1 rack temperature raw": "iso.3.6.1.4.1.318.1.1.10.2.3.2.1.4.1"
    }
))

conf.add(SNMP(
    host="usv2.mgmt.selfnet.de",
    oids={
        "usv2 current raw": "iso.3.6.1.4.1.318.1.1.1.4.3.4.0",
        "usv2 rack temperature raw": "iso.3.6.1.4.1.318.1.1.10.2.3.2.1.4.1"
    }
))   

conf.add(SNMP(
    host="usv3.mgmt.selfnet.de",
    oids={
        "usv3 current raw": "iso.3.6.1.4.1.318.1.1.1.4.3.4.0",
        "usv3 rack temperature raw": "iso.3.6.1.4.1.318.1.1.10.2.3.2.1.4.1"
    }
))   


# divide USV current by 10
divide_by_ten = lambda x: float(x)/10

conf.add(SimpleConversion( name="usv1 current", source="usv1 current raw", func=divide_by_ten))
conf.add(SimpleConversion( name="usv2 current", source="usv2 current raw", func=divide_by_ten))
conf.add(SimpleConversion( name="usv3 current", source="usv3 current raw", func=divide_by_ten))

# rack temperature as integer
conf.add(SimpleConversion(name="usv1 rack temperature", source="usv1 rack temperature raw", func=int))
conf.add(SimpleConversion(name="usv2 rack temperature", source="usv2 rack temperature raw", func=int))
conf.add(SimpleConversion(name="usv3 rack temperature", source="usv3 rack temperature raw", func=int))

