conf.add(Munin(
    name="accesses www",
    host="www",
    identifier="apache_accesses",
    key="accesses80"
))

conf.add(PerSecond(
    name="accesses per second www",
    sources=["accesses www"]
))
    
