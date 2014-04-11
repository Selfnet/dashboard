Dashboard
=========

Dashboard for live monitoring of all kinds of foo.


## WIP
This is WORK IN PROGRESS. It's not finished or usable in any way.

## Description

The daemon spawns threads that fetch data (e.g., via SNMP or HTTP). Every threads works for itself, so they can get out of sync. Some threads trigger their updates in a given interval, or on updates in the redis database. Interval and the data to be aggregated is specified in the config.py file. The builtin flask webserver provides the website and the data to display for the clients.

## Dependencies

* Backend
 * python3
 * python3-redis (and a redis server)
 * optional: snmpget, snmpbulkwalk, ping, curl
