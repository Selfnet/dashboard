from dash.sources import SNMPWalkSum

conf.add(SNMPWalkSum(
    name="noc wlan clients",
    host="wlc.noc.selfnet.de",
    oid="iso.3.6.1.4.1.14525.4.5.1.1.2.1.16.12.109.103.48.50.49.49.53.49"
))
    
