# DASHBOARD CONF
#
#
#
# SETTINGS
#
# Global backend settings are in the "settings" dict.
# Keys:
#   memcache_servers:
#       list of memcache servers, i.e. ["host:port"]
#   interval:
#       number of seconds between refresh cycles
#
#
#
# DATASETS
#
# Define a number of datasets and add them to the "poll" list
# in the order in which they shall be updated. You can also add
# datasets that combine or transform existing datasets. Make sure
# you poll them *after* the source dataset. Add sets you want to be
# published to the "publish" dict (name:dataset pairs).

from dataset import *



length = 1080
interval = 10


settings = {
    "memcache_servers": ["127.0.0.1:11211"],
    "interval": interval, # update interval # seconds
}

poll = []
publish = {}






# DATASET DECLARATIONS

# misc (wireless lan, rt tickets, ...)

nocWlan = SimpleSNMP(
    host="10.0.2.1",
    oid="iso.3.6.1.4.1.14525.4.5.1.1.2.1.16.12.109.103.48.50.49.49.53.49.51.52.48.48",
    length=length,
    unit="clients online"
)
poll.append(nocWlan)
publish["NOC WLAN Clients"] = nocWlan

rtTickets = SimpleHTTP(
    url="https://roundcube.selfnet.de/tickets.php",
    length=length,
    unit="tickets"
)
poll.append(rtTickets)
publish["open rt tickets"] = rtTickets

userVpnConnections = SimpleSNMP(
    host="10.0.2.21",
    oid="1.3.6.1.4.1.9.9.392.1.3.3.0",
    length=length,
    unit="connections"
)
poll.append(userVpnConnections)
publish["user vpn connections"] = userVpnConnections


# traffic border routers <-> internet

stuwost1_belwue = SimpleSNMP(
    host="stuwost1",
    oid=".1.3.6.1.2.1.31.1.1.1.10.570",
    length=2,
    unit="octets"
)
poll.append(stuwost1_belwue)

belwue_stuwost1 = SimpleSNMP(
    host="stuwost1",
    oid=".1.3.6.1.2.1.31.1.1.1.6.570",
    length=2,
    unit="octets"
)
poll.append(belwue_stuwost1)

stuwost2_belwue = SimpleSNMP(
    host="stuwost2",
    oid=".1.3.6.1.2.1.31.1.1.1.10.566",
    length=2,
    unit="octets"
)
poll.append(stuwost2_belwue)

belwue_stuwost2 = SimpleSNMP(
    host="stuwost2",
    oid=".1.3.6.1.2.1.31.1.1.1.6.566",
    length=2,
    unit="octets"
)
poll.append(belwue_stuwost2)

stuwost1_belwue_v6only = SimpleSNMP(
    host="stuwost1",
    oid=".1.3.6.1.4.1.2636.3.11.1.3.1.1.2.570",
    length=2,
    unit="octets"
)
poll.append(stuwost1_belwue_v6only)

belwue_stuwost1_v6only = SimpleSNMP(
    host="stuwost1",
    oid=".1.3.6.1.4.1.2636.3.11.1.3.1.1.1.570",
    length=2,
    unit="octets"
)
poll.append(belwue_stuwost1_v6only)

stuwost2_belwue_v6only = SimpleSNMP(
    host="stuwost2",
    oid=".1.3.6.1.4.1.2636.3.11.1.3.1.1.2.566",
    length=2,
    unit="octets"
)
poll.append(stuwost2_belwue_v6only)

belwue_stuwost2_v6only = SimpleSNMP(
    host="stuwost2",
    oid=".1.3.6.1.4.1.2636.3.11.1.3.1.1.1.566",
    length=2,
    unit="octets"
)
poll.append(belwue_stuwost2_v6only)


# traffic LANs <-> border routers

#wh_stuwost1 = SimpleSNMP(
#    host="stuwost1",
#    oid=".1.3.6.1.2.1.31.1.1.1.6.571",
#    length=2,
#    unit="octets"
#)
#poll.append(wh_stuwost1)
#
#stuwost1_wh = SimpleSNMP(
#    host="stuwost1",
#    oid=".1.3.6.1.2.1.31.1.1.1.10.571",
#    length=2,
#    unit="octets"
#)
#poll.append(stuwost1_wh)

selfnet_stuwost1 = SimpleSNMP(
    host="stuwost1",
    oid=".1.3.6.1.2.1.31.1.1.1.6.578",
    length=2,
    unit="octets"
)
poll.append(selfnet_stuwost1)

stuwost1_selfnet = SimpleSNMP(
    host="stuwost1",
    oid=".1.3.6.1.2.1.31.1.1.1.10.578",
    length=2,
    unit="octets"
)
poll.append(stuwost1_selfnet)

selfnet_stuwost2 = SimpleSNMP(
    host="stuwost2",
    oid=".1.3.6.1.2.1.31.1.1.1.6.580",
    length=2,
    unit="octets"
)
poll.append(selfnet_stuwost2)

stuwost2_selfnet = SimpleSNMP(
    host="stuwost2",
    oid=".1.3.6.1.2.1.31.1.1.1.10.580",
    length=2,
    unit="octets"
)
poll.append(stuwost2_selfnet)

selfnet_stuwost1_v6only = SimpleSNMP(
    host="stuwost1",
    oid=".1.3.6.1.4.1.2636.3.11.1.3.1.1.1.578",
    length=2,
    unit="octets"
)
poll.append(selfnet_stuwost1_v6only)

stuwost1_selfnet_v6only = SimpleSNMP(
    host="stuwost1",
    oid=".1.3.6.1.4.1.2636.3.11.1.3.1.1.2.578",
    length=2,
    unit="octets"
)
poll.append(stuwost1_selfnet_v6only)

selfnet_stuwost2_v6only = SimpleSNMP(
    host="stuwost2",
    oid=".1.3.6.1.4.1.2636.3.11.1.3.1.1.1.580",
    length=2,
    unit="octets"
)
poll.append(selfnet_stuwost2_v6only)

stuwost2_selfnet_v6only = SimpleSNMP(
    host="stuwost2",
    oid=".1.3.6.1.4.1.2636.3.11.1.3.1.1.2.580",
    length=2,
    unit="octets"
)
poll.append(stuwost2_selfnet_v6only)


# received routes (on border routers)

routes_stuwost1_v4 = SimpleSNMP(
    host="stuwost1",
    oid="iso.3.6.1.4.1.2636.5.1.1.2.6.2.1.8.0.1.1",
    length=length,
    unit="routes"
)
poll.append(routes_stuwost1_v4)
publish["stuwost1 received routes ipv4"] = routes_stuwost1_v4

routes_stuwost1_v6 = SimpleSNMP(
    host="stuwost1",
    oid="iso.3.6.1.4.1.2636.5.1.1.2.6.2.1.8.1.2.1",
    length=length,
    unit="routes"
)
poll.append(routes_stuwost1_v6)
publish["stuwost1 received routes ipv6"] = routes_stuwost1_v6

routes_stuwost2_v4 = SimpleSNMP(
    host="stuwost2",
    oid="iso.3.6.1.4.1.2636.5.1.1.2.6.2.1.8.0.1.1",
    length=length,
    unit="routes"
)
poll.append(routes_stuwost2_v4)
publish["stuwost2 received routes ipv4"] = routes_stuwost2_v4

routes_stuwost2_v6 = SimpleSNMP(
    host="stuwost2",
    oid="iso.3.6.1.4.1.2636.5.1.1.2.6.2.1.8.1.2.1",
    length=length,
    unit="routes"
)
poll.append(routes_stuwost2_v6)
publish["stuwost2 received routes ipv6"] = routes_stuwost2_v6







# COMBINING, TRANSFORMING, ...

# border routers <-> internet
rate_stuwost1_belwue = OctetsToBps(stuwost1_belwue, length=length, interval=interval)
rate_stuwost2_belwue = OctetsToBps(stuwost2_belwue, length=length, interval=interval)
rate_belwue_stuwost1 = OctetsToBps(belwue_stuwost1, length=length, interval=interval)
rate_belwue_stuwost2 = OctetsToBps(belwue_stuwost2, length=length, interval=interval)

poll.append(rate_stuwost1_belwue)
poll.append(rate_stuwost2_belwue)
poll.append(rate_belwue_stuwost1)
poll.append(rate_belwue_stuwost2)

publish["stuwost1 uplink out"] = rate_stuwost1_belwue
publish["stuwost2 uplink out"] = rate_stuwost2_belwue
publish["stuwost1 uplink in"]  = rate_belwue_stuwost1
publish["stuwost2 uplink in"]  = rate_belwue_stuwost2


# border router <-> internet (IPv6 only)
rate_stuwost1_belwue_v6only = OctetsToBps(stuwost1_belwue_v6only, length=length, interval=interval)
rate_stuwost2_belwue_v6only = OctetsToBps(stuwost2_belwue_v6only, length=length, interval=interval)
rate_belwue_stuwost1_v6only = OctetsToBps(belwue_stuwost1_v6only, length=length, interval=interval)
rate_belwue_stuwost2_v6only = OctetsToBps(belwue_stuwost2_v6only, length=length, interval=interval)

poll.append(rate_stuwost1_belwue_v6only)
poll.append(rate_stuwost2_belwue_v6only)
poll.append(rate_belwue_stuwost1_v6only)
poll.append(rate_belwue_stuwost2_v6only)

publish["stuwost1 uplink ipv6 out"] = rate_stuwost1_belwue_v6only
publish["stuwost2 uplink ipv6 out"] = rate_stuwost2_belwue_v6only
publish["stuwost1 uplink ipv6 in"]  = rate_belwue_stuwost1_v6only
publish["stuwost2 uplink ipv6 in"]  = rate_belwue_stuwost2_v6only


# WH-Netz <-> border router
#rate_wh_stuwost1 = OctetsToBps(wh_stuwost1, length=length, interval=interval)
#rate_stuwost1_wh = OctetsToBps(stuwost1_wh, length=length, interval=interval)
#
#poll.append(rate_wh_stuwost1)
#poll.append(rate_stuwost1_wh)
#
#publish["wh-netz uplink out"] = rate_wh_stuwost1
#publish["wh-netz uplink in"]  = rate_stuwost1_wh


# Selfnet <-> border routers
rate_selfnet_stuwost1 = OctetsToBps(selfnet_stuwost1, length=1, interval=interval)
rate_selfnet_stuwost2 = OctetsToBps(selfnet_stuwost2, length=1, interval=interval)
rate_stuwost1_selfnet = OctetsToBps(stuwost1_selfnet, length=1, interval=interval)
rate_stuwost2_selfnet = OctetsToBps(stuwost2_selfnet, length=1, interval=interval)

poll.append(rate_selfnet_stuwost1)
poll.append(rate_selfnet_stuwost2)
poll.append(rate_stuwost1_selfnet)
poll.append(rate_stuwost2_selfnet)

# combine traffic from both border routers
rate_selfnet_belwue = Add([rate_selfnet_stuwost1, rate_selfnet_stuwost2], length=length)
rate_belwue_selfnet = Add([rate_stuwost1_selfnet, rate_stuwost2_selfnet], length=length)

poll.append(rate_selfnet_belwue)
poll.append(rate_belwue_selfnet)

publish["selfnet uplink out"] = rate_selfnet_belwue
publish["selfnet uplink in"]  = rate_belwue_selfnet


# Selfnet <-> border routers (IPv6 only)
rate_selfnet_stuwost1_v6only = OctetsToBps(selfnet_stuwost1_v6only, length=1, interval=interval)
rate_selfnet_stuwost2_v6only = OctetsToBps(selfnet_stuwost2_v6only, length=1, interval=interval)
rate_stuwost1_selfnet_v6only = OctetsToBps(stuwost1_selfnet_v6only, length=1, interval=interval)
rate_stuwost2_selfnet_v6only = OctetsToBps(stuwost2_selfnet_v6only, length=1, interval=interval)

poll.append(rate_selfnet_stuwost1_v6only)
poll.append(rate_selfnet_stuwost2_v6only)
poll.append(rate_stuwost1_selfnet_v6only)
poll.append(rate_stuwost2_selfnet_v6only)

# combine traffic from both border routers
rate_selfnet_belwue_v6only = Add([rate_selfnet_stuwost1_v6only, rate_selfnet_stuwost2_v6only], length=length)
rate_belwue_selfnet_v6only = Add([rate_stuwost1_selfnet_v6only, rate_stuwost2_selfnet_v6only], length=length)

poll.append(rate_selfnet_belwue_v6only)
poll.append(rate_belwue_selfnet_v6only)

publish["selfnet uplink ipv6 out"] = rate_selfnet_belwue_v6only
publish["selfnet uplink ipv6 in"]  = rate_belwue_selfnet_v6only


# Internet uplink total
rate_to_belwue   = Add([rate_stuwost1_belwue, rate_stuwost2_belwue], length=length)
rate_from_belwue = Add([rate_belwue_stuwost1, rate_belwue_stuwost2], length=length)

poll.append(rate_to_belwue)
poll.append(rate_from_belwue)

publish["belwue uplink in"]  = rate_from_belwue
publish["belwue uplink out"] = rate_to_belwue


# USV
usv1_current = SimpleSNMP(
    host="usv1.mgmt.selfnet.de",
    oid="iso.3.6.1.4.1.318.1.1.1.4.3.4.0",
    length=1,
    unit="deciampere"
)

usv2_current = SimpleSNMP(
    host="usv2.mgmt.selfnet.de",
    oid="iso.3.6.1.4.1.318.1.1.1.4.3.4.0",
    length=1,
    unit="deciampere"
)

poll.append(usv1_current)
poll.append(usv2_current)

usv1_current_formatted = Divide(usv1_current, 10, length=length, unit="ampere")
usv2_current_formatted = Divide(usv2_current, 10, length=length, unit="ampere")

poll.append(usv1_current_formatted)
poll.append(usv2_current_formatted)

publish["usv1 current"] = usv1_current_formatted
publish["usv2 current"] = usv2_current_formatted


# TEMPERATURE
rack1_temp = SimpleSNMP(
    host="usv1.mgmt.selfnet.de",
    oid="1.3.6.1.4.1.318.1.1.10.2.3.2.1.4.1",
    length=length,
    unit="degrees celsius"
)
poll.append(rack1_temp)
publish["rack 1 temperature"] = rack1_temp

rack2_temp = SimpleSNMP(
    host="usv2.mgmt.selfnet.de",
    oid="1.3.6.1.4.1.318.1.1.10.2.3.2.1.4.1",
    length=length,
    unit="degrees celsius"
)
poll.append(rack2_temp)
publish["rack 2 temperature"] = rack2_temp

