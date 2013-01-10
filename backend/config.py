config = {
    "memcache_servers": ['127.0.0.1:11211'],
    "interval": 10, # update interval # seconds
    "maxvalues": 180 # number of values to be stored in cache # 10*180 = 30min
}

charts = [{
        "name": "Internet (Selfnet + WH-Netz)",
        "graphs": [{
            "name": "Upstream",
            "dataset": "belwue uplink out"
            },{
            "name": "Downstream",
            "dataset": "belwue uplink in"
        }],
        "unit": "bits per second",
        "maxvalues": 90 # 90 values * 10sec = 15min history
    },{
        "name": "Selfnet",
        "graphs": [{
            "name": "Upstream",
            "dataset": "selfnet uplink out"
            },{
            "name": "Downstream",
            "dataset": "selfnet uplink in"
        }],
        "unit": "bits per second",
        "maxvalues": 90 # 90 values * 10sec = 15min history
    },{
        "name": "Selfnet, IPv6 only",
        "graphs": [{
            "name": "Upstream",
            "dataset": "selfnet uplink ipv6 out"
            },{
            "name": "Downstream",
            "dataset": "selfnet uplink ipv6 in"
        }],
        "unit": "bits per second",
        "maxvalues": 90 # 90 values * 10sec = 15min history
    },{
        "name": "WH-Netz",
        "graphs": [{
            "name": "Upstream",
            "dataset": "wh-netz uplink out"
            },{
            "name": "Downstream",
            "dataset": "wh-netz uplink in"
        }],
        "unit": "bits per second",
        "maxvalues": 90 # 90 values * 10sec = 15min history
    },{
        "name": "NOC WLAN Clients",
        "graphs": [{
            "name": "clients online",
            "dataset": "NOC WLAN Clients"
        }],
        "unit": "connected clients",
        "maxvalues": 90 # 90 values * 10sec = 15min history
    },{
        "name": "RT Tickets",
        "graphs": [{
            "name": "open tickets",
            "dataset": "open rt tickets"
        }],
        "unit": "tickets",
        "maxvalues": 90 # 90 values * 10sec = 15min history
    }
]

datasets = {
    "NOC WLAN Clients": {
        "type": "snmp",
        "targets": [{
            "host": "10.43.224.1",
            "oid": "iso.3.6.1.4.1.14525.4.5.1.1.2.1.16.12.109.103.48.50.49.49.53.49.51.52.49.53",
            "factor": 1,
            "cumulative": False
        }],
        "unit": "clients online"
    },
    "open rt tickets": {
        "type": "http",
        "url": "https://roundcube.selfnet.de/tickets.php",
        "factor": 1,
        "cumulative": False,
        "unit": "tickets"
    },
    "belwue uplink out": {
        "type": "snmp",
        "targets": [{
            "host": "stuwost1",
            "oid": ".1.3.6.1.2.1.31.1.1.1.10.570",
            "factor": 8,
            "cumulative": True
        },{
            "host": "stuwost2",
            "oid": ".1.3.6.1.2.1.31.1.1.1.10.566",
            "factor": 8,
            "cumulative": True
        }],
        "unit": "bits per second"
    },
    "belwue uplink in": {
        "type": "snmp",
        "targets": [{
            "host": "stuwost1",
            "oid": ".1.3.6.1.2.1.31.1.1.1.6.570",
            "factor": 8,
            "cumulative": True
        },{
            "host": "stuwost2",
            "oid": ".1.3.6.1.2.1.31.1.1.1.6.566",
            "factor": 8,
            "cumulative": True
        }],
        "unit": "bits per second"
    },
    "wh-netz uplink out": {
        "type": "snmp",
        "targets": [{
            "host": "stuwost1",
            "oid": ".1.3.6.1.2.1.31.1.1.1.6.571",
            "factor": 8,
            "cumulative": True
        }],
        "unit": "bits per second"
    },
    "wh-netz uplink in": {
        "type": "snmp",
        "targets": [{
            "host": "stuwost1",
            "oid": ".1.3.6.1.2.1.31.1.1.1.10.571",
            "factor": 8,
            "cumulative": True
        }],
        "unit": "bits per second"
    },
    "selfnet uplink out": {
        "type": "snmp",
        "targets": [{
            "host": "stuwost2",
            "oid": ".1.3.6.1.2.1.31.1.1.1.6.580",
            "factor": 8,
            "cumulative": True
        },{
            "host": "stuwost1",
            "oid": ".1.3.6.1.2.1.31.1.1.1.6.578",
            "factor": 8,
            "cumulative": True
        }],
        "unit": "bits per second"
    },
    "selfnet uplink in": {
        "type": "snmp",
        "targets": [{
            "host": "stuwost2",
            "oid": ".1.3.6.1.2.1.31.1.1.1.10.580",
            "factor": 8,
            "cumulative": True
        },{
            "host": "stuwost1",
            "oid": ".1.3.6.1.2.1.31.1.1.1.10.578",
            "factor": 8,
            "cumulative": True
        }],
        "unit": "bits per second"
    },
    "selfnet uplink ipv6 out": {
        "type": "snmp",
        "targets": [{
            "host": "stuwost1",
            "oid": ".1.3.6.1.4.1.2636.3.11.1.3.1.1.1.578",
            "factor": 8,
            "cumulative": True
        },{
            "host": "stuwost2",
            "oid": ".1.3.6.1.4.1.2636.3.11.1.3.1.1.1.580",
            "factor": 8,
            "cumulative": True
        }],
        "unit": "bits per second"
    },
    "selfnet uplink ipv6 in": {
        "type": "snmp",
        "targets": [{
            "host": "stuwost1",
            "oid": ".1.3.6.1.4.1.2636.3.11.1.3.1.1.2.578",
            "factor": 8,
            "cumulative": True
        },{
            "host": "stuwost2",
            "oid": ".1.3.6.1.4.1.2636.3.11.1.3.1.1.2.580",
            "factor": 8,
            "cumulative": True
        }],
        "unit": "bits per second"
    }
}

