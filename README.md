Dashboard
=========

Dashboard for our NOC


## Description

The backend (dash.py) fetches data (e.g., via SNMP or HTTP) in a given interval. Interval and the data to be aggregated is specified in the config.py file. After each update cycle the datasets are combined in a python dict and written to memcache. The cgi scripts provide a way to access the data inside memcache.
Additionally the web-frontend dynamically parses the json-formatted datasets and builds the charts using the highcharts library.

## Dependencies

* Backend
 * Python
 * python-memcache
 * for SNMP Data: snmpget
 * a webserver with python cgi
* web-frontend
 * highcharts.js
 * jquery.min.js

