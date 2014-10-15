Dashboard
=========

Dashboard for live monitoring of all kinds of foo.


## WIP
This is WORK IN PROGRESS. It's not finished or usable in any way.

## Description

The daemon spawns threads that fetch data (e.g., via SNMP or HTTP). Every threads works for itself, so they can get out of sync. Some threads trigger their updates in a given interval, or on updates in the redis database. Interval and the data to be aggregated is specified in the config.py file. The builtin server provides static websites and websockets that push new data to the clients.

## Dependencies

  * python3
  * redis-server (version >= 2.8 for PubSub features)
  * python3-redis
  * optional: snmpget, snmpbulkwalk, ping, curl

## How it works

The server spawns a number of threads, one for each configured data source. The threads run asynchronously and fetch updates in their own interval. The data is then written to the redis key-value store with a value and a timesta
mp. Some data sources don't run updates in a configured interval, but listen on updates for existing datasets. This comes in handy, whenever you need data in a different format, combine previous values (difference, average, etc.), or combine data from multiple sources.

The website is delivered by a webserver (static files) or the dashboard itself. The javascript classes provide an interface that you can use to spawn charts that listen on updates and update automatically. The chart data is provided via websockets. If datasets are updated, the server pushes those updates to the clients using those websockets.

## Installation / How To

  1. Checkout the git and install the dependencies. You might want to use virtualenv, especially on debian, where all the packets are 100 years old and lack of features needed here.
  2. Configure the server. There's an example configuration in conf.d.example that you can use. Take a look at the "cusesection below aswell.
  3. Change the html files to suit your needs. The "source" for the datasets has to be the name of your datasets in the servers configuration.
  4. Run the dashboard and have fun.

## Configuration

On startup, all the YAML files in conf.d are parsed and merged. Startup of the dashboard will fail, if there are merge conflicts (i.e., the same parameter is configured twice in two files, but with different values).

For source objects, the software will search for parameters in the corresponding object config first, then in the class defaults, in the global defaults and finally in the hardcoded defaults (if there is one for the given parameter). If a parameter is required, but not configured, an exception will be raised. This scheme allows you for example to configure a default interval for all updates, but override it for a certain class, e.g., to schedule updates for SNMP sources less frequent, to avoid issues with SNMP rate limiting.

## Writing Own Extensions

Writing own data sources is easy. You can simply write classes that inherit from TimedSource (triggers updates with a timer, configured by the "timeout" parameter) or from PubSubSource (triggers updates when a source dataset, configured in the "source" parameter, gets updated). Both are subclasses of Source (all of them in source/base.py) which already provides some helpful functions:

  * .poll(self) for TimedSource and .update(self) for PubSubSource - create this to do whatever your source needs to do
  * .get_config(name, default=None) - returns a configured value, or the default, or raises an AttributeError
  * .push(value, name=None, timestamp=None) - write a time-value pair to the database, default name comes from the configuration, default timestamp is the current time, values will be typecastet to "type" (from the builtins, default is "str", since redis stores values as strings anyway)
  * .pull(n=1, name=None) - pull time-value pairs from the db, default is one pair (the most recent) from the configured name, but you could also pull the last 10 values for the set "foo"
  * .typecast(value, default_type=None) - typecast a value to some built-in type
