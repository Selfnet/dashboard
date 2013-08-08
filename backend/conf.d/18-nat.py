conf.add(Munin(
    name="cgn flows patty",
    host="patty",
    cmd="fetch fw_conntrack\nquit",
    key="total"
))

conf.add(Munin(
    name="cgn flows marge",
    host="marge",
    cmd="fetch fw_conntrack\nquit",
    key="total"
))

