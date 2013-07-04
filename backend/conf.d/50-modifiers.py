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
