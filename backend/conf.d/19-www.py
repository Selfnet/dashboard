conf.add(Munin(
    name="accesses www",
    host="www",
    cmd="fetch apache_accesses\nquit",
    key="accesses80"
))

conf.add(PerSecond(
    name="accesses per second www",
    sources=["accesses www"]
))
    
