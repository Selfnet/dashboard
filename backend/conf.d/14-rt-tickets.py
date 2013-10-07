conf.add(HTTP(
    "open selfnet rt tickets raw",
    "https://rt.selfnet.de:444/tickets.pl",
    int
))

conf.add(HTTP(
    "open wh-netz rt tickets raw",
    "https://rt.selfnet.de:444/tickets-wh.pl",
    int
))

