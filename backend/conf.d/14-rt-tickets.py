from dash.sources import HTTP
from dash.conversions import SimpleConversion

conf.add(HTTP("open rt tickets raw", "https://rt.selfnet.de:444/tickets.pl"))

# convert to integer
conf.add(SimpleConversion(source="open rt tickets raw", name="open rt tickets", func=int))
