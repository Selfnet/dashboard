conf.add(SNMP(
    host="usv1.mgmt.selfnet.de",
    mibs={
        "usv1 current": "iso.3.6.1.4.1.318.1.1.1.4.3.4.0",
        "usv1 rack temperature": "1.3.6.1.4.1.318.1.1.10.2.3.2.1.4.1"
    }
))

conf.add(SNMP(
    host="usv2.mgmt.selfnet.de",
    mibs={
        "usv2 current": "iso.3.6.1.4.1.318.1.1.1.4.3.4.0",
        "usv2 rack temperature": "1.3.6.1.4.1.318.1.1.10.2.3.2.1.4.1"
    }
))   
