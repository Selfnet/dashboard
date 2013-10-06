conf.add(Ping(name="ping 8.8.8.8", target="8.8.8.8"))
conf.add(Ping6(name="ping6 2001:4860:4860::8888", target="2001:4860:4860::8888"))

conf.add(Ping(name="ping www.heise.de", target="www.heise.de"))
conf.add(Ping6(name="ping6 www.heise.de", target="www.heise.de"))

conf.add(Ping(name="ping www.belwue.de", target="www.belwue.de"))
conf.add(Ping6(name="ping6 www.belwue.de", target="www.belwue.de"))

conf.add(Ping(name="ping www.selfnet-status.de", target="www.selfnet-status.de"))
conf.add(Ping6(name="ping6 www.selfnet-status.de", target="www.selfnet-status.de"))

conf.add(Ping(name="ping vpn heuss", target="eliza.server.selfnet.de"))
conf.add(Ping6(name="ping6 vpn heuss", target="eliza.server.selfnet.de"))

conf.add(Ping(name="ping vpn kade", target="jones.server.selfnet.de"))
conf.add(Ping6(name="ping6 vpn kade", target="jones.server.selfnet.de"))

conf.add(Ping(name="ping vpn axa", target="hugo.server.selfnet.de"))
conf.add(Ping6(name="ping6 vpn axa", target="hugo.server.selfnet.de"))

conf.add(Ping(name="ping vpn moehringen", target="cyrus.server.selfnet.de"))
#conf.add(Ping6(name="ping6 vpn moehringen", target="cyrus.server.selfnet.de"))

conf.add(Ping(name="ping switch schwabengarage", target="sg-1.lan.selfnet.de"))
conf.add(Ping6(name="ping6 switch schwabengarage", target="sg-1.lan.selfnet.de"))

