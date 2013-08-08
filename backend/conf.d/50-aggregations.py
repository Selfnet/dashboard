from dash.conversions import *

conf.add(OctetsToBitrate(
    name="bps to belwue",
    sources=[
        "octets stuwost1 to belwue",
        "octets stuwost2 to belwue"
    ]
))

conf.add(OctetsToBitrate(
    name="bps from belwue",
    sources=[
        "octets belwue to stuwost1",
        "octets belwue to stuwost2"
    ]
))


conf.add(OctetsToBitrate(
    name="bps to belwue ipv6 only",
    sources=[
        "octets stuwost1 to belwue ipv6",
        "octets stuwost2 to belwue ipv6"
    ]
))

conf.add(OctetsToBitrate(
    name="bps from belwue ipv6 only",
    sources=[
        "octets belwue to stuwost1 ipv6",
        "octets belwue to stuwost2 ipv6"
    ]
))

conf.add(Percentage(
    name="percentage ipv6 from belwue",
    value="bps from belwue ipv6 only",
    maximum="bps from belwue"
))
        
conf.add(Percentage(
    name="percentage ipv6 to belwue",
    value="bps to belwue ipv6 only",
    maximum="bps to belwue"
))



conf.add(Sum(
    name="total octets selfnet to belwue",
    sources=[
        "octets stuwost1 to belwue",
        "octets stuwost2 to belwue"
    ]
))

conf.add(Sum(
    name="total octets belwue to selfnet",
    sources=[
        "octets belwue to stuwost1",
        "octets belwue to stuwost2"
    ]
))


