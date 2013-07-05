from dash.sources import HTTP
from dash.conversions import SimpleConversion

conf.add(HTTP("open selfnet rt tickets raw", "https://rt.selfnet.de:444/tickets.pl"))
conf.add(HTTP("open wh-netz rt tickets raw", "https://rt.selfnet.de:444/tickets-wh.pl"))

# convert to integer
conf.add(SimpleConversion(source="open selfnet rt tickets raw", name="open selfnet rt tickets", func=int))
conf.add(SimpleConversion(source="open wh-netz rt tickets raw", name="open wh-netz rt tickets", func=int))
