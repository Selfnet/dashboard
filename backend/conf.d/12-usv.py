# divide USV current by 10
divide_by_ten = lambda x: float(x)/10


conf.add(SNMP(
    host="usv1.mgmt.selfnet.de",
    oids={
        "usv1 current": ("iso.3.6.1.4.1.318.1.1.1.4.3.4.0", divide_by_ten),
        "usv1 rack temperature": ("iso.3.6.1.4.1.318.1.1.10.2.3.2.1.4.1", int)
    }
))

conf.add(SNMP(
    host="usv2.mgmt.selfnet.de",
    oids={
        "usv2 current": ("iso.3.6.1.4.1.318.1.1.1.4.3.4.0", divide_by_ten),
        "usv2 rack temperature": ("iso.3.6.1.4.1.318.1.1.10.2.3.2.1.4.1", int)
    }
))   

conf.add(SNMP(
    host="usv3.mgmt.selfnet.de",
    oids={
        "usv3 current": ("iso.3.6.1.4.1.318.1.1.1.4.3.4.0", divide_by_ten),
        "usv3 rack temperature": ("iso.3.6.1.4.1.318.1.1.10.2.3.2.1.4.1", int)
    }
))   

conf.add(SNMP(
    version = '1',
    host="10.0.15.2",
    oids={
        "usv4 current": ("iso.3.6.1.2.1.33.1.4.4.1.3.1", divide_by_ten),
        "usv4 rack temperature": ("iso.3.6.1.4.1.705.1.8.1.0", divide_by_ten)
    }
))
