conf.add(SNMP(
    host="usv1.mgmt.selfnet.de",
    oids={
        "usv1 current": "iso.3.6.1.4.1.318.1.1.1.4.3.4.0",
        "usv1 rack temperature": "iso.3.6.1.4.1.318.1.1.10.2.3.2.1.4.1"
    }
))

conf.add(SNMP(
    host="usv2.mgmt.selfnet.de",
    oids={
        "usv2 current": "iso.3.6.1.4.1.318.1.1.1.4.3.4.0",
        "usv2 rack temperature": "iso.3.6.1.4.1.318.1.1.10.2.3.2.1.4.1"
    }
))   

conf.add(SNMP(
    host="usv3.mgmt.selfnet.de",
    oids={
        "usv3 current": "iso.3.6.1.4.1.318.1.1.1.4.3.4.0",
        "usv3 rack temperature": "iso.3.6.1.4.1.318.1.1.10.2.3.2.1.4.1"
    }
))   
