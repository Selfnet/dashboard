conf.add(Munin(
    name="cgn flows patty",
    host="patty",
    identifier="fw_conntrack",
    key="total"
))

conf.add(Munin(
    name="cgn flows marge",
    host="marge",
    identifier="fw_conntrack",
    key="total"
))

