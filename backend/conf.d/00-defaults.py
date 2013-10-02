# general settings
#conf.interval = 10
#conf.threads = None # ==> use the number of sources

conf.set_loglevel("INFO")
conf.add_logfile("dash.log", "WARNING")

# defaultss
conf.defaults["snmp port"] = 161
conf.defaults["snmp version"] = 2
conf.defaults["snmp community"] = "public"

conf.defaults["dataset size"] = 1080

conf.defaults["munin timeout"] = 1.5

