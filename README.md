Dashboard
=========

Dashboard for live monitoring of all kinds of foo.


## WIP
This is WORK IN PROGRESS. It's not finished or usable in any way.

## Description

Main focus lies on the backend, which spawns lots of threads that gather data from different sources. The backend can be queried for time-value data points. A simple javascript library and webpage example is included. It connects to the tornado websocket backend and updates the charts with real-time data.

This project is meant to enable others to work with the data provided by the dashboard backend, write new source modules, or write new frontends.


## Dependencies

  * basics
    * python3
    * linux-based OS
  * optional data sources
    * snmpget/snmpbulkwalk
    * ping
    * curl
  * optional data output
    * tornado
  * optional web-frontend
    * highcharts
    * jquery


## How it works

The server spawns a number of threads, one for each configured data source. The threads run asynchronously and fetch updates in their own interval. The data is then written to the key-value store as the value and a timestamp. Some data sources don't run updates in a configured interval, but listen on updates for existing datasets. This comes in handy, whenever you need data in a different format, combine previous values (difference, average, etc.), or combine data from multiple sources.

The website should be delivered by a webserver (static files), so the dashboard only needs to run the websockets or REST API. The javascript classes provide an interface that you can use to spawn charts that listen on updates and update automatically. The chart data is provided via websockets. If datasets are updated, the server pushes those updates to the clients using those websockets.


## Installation / How To

  1. Checkout the git and install the dependencies.
  2. Configure the server. There's an example configuration in conf.d.example that you can use. Take a look at the "Configuration" Section below aswell.
  3. Change the html files to suit your needs. Get yourself a nice looking page. The "source" for the datasets has to be the name of your datasets in the servers configuration.
  4. Run the dashboard and have fun.


## Configuration

On startup, all the YAML files in conf.d are parsed and merged. Startup of the dashboard will fail, if there are merge conflicts (i.e., the same parameter is configured twice in two files, but with different values).

For source objects, the software will search for parameters in the corresponding object config first, then in the class defaults, in the global defaults and finally in the hardcoded defaults (if there is one for the given parameter). If a parameter is required, but not configured, an exception will be raised. This scheme allows you for example to configure a default interval for all updates, but override it for a certain class, e.g., to schedule updates for SNMP sources less frequent, to avoid issues with SNMP rate limiting. And you can configure another interval for a certain worker, which comes in handy for the PersistentStorage object, which you may want to run only every few minutes.

Here's the class structure for the available workers:

<pre>
Worker
|-- Websocket
|-- REST
`-- Source
    |-- PubSubSource
    |   |-- Factor
    |   |-- OctetsToBps
    |   `-- Sum
    `-- TimedSource
        |-- Cmd
        |-- HTTPGet
        |-- Munin
        |-- Ping
        |-- SNMPGet
        `-- SNMPWalkSum
</pre>

The TimedSource classes run every $interval seconds. The PubSubSources update either when their first data source is updated, or when either of the sources is updated.

Here are the possible basic configuration options. Keep in mind that all options can be defnied in the defaults, class defaults, or for an object itself:

  * Source (base class for all sources)
    * name: name for the dataset (subclasses might override this, e.g., to write multiple sets)
    * values: number of values to store in db
    * typecast: optional, python3 builtin type
  * TimedSource
    * interval: number of seconds between updates
  * PubSubSource
    * subscribe: run an update when [first (default), all] sources are updated

## Writing Own Modules

Writing own data sources is easy. You can simply write classes that inherit from TimedSource (triggers updates with a timer, configured by the "timeout" parameter) or from PubSubSource (triggers updates when a source dataset, configured in the "source" parameter, gets updated). Both are subclasses of Source (all of them in source/base.py) which already provides some helpful functions:

  * `.poll(self)` for TimedSource - will be called every time the timer fires
  * `.update(self)` for PubSubSource - will be called every time a subscribed dataset changed
  * `.get_config(name, default=None)` - returns a configured value, or the default, or raises an AttributeError
  * `.push(value, name=None, timestamp=None)` - write a time-value pair to the database, default name comes from `get_config("name")`, default timestamp is the current time, values will be typecastet to "type" (if set).
  * `.pull(n=1, name=None)` - pull time-value pairs from the db, default is one pair (the most recent) from the configured name, but you could also pull the last 10 values for the set "foo"
  * `.typecast(value, default_type=None)` - typecast a value to some built-in type

You can also refer to simple existing modules like the one in `modules/file.py` and use them as examples.

### Module Example

A simple example for a TimedSource:
```python
import random
from .base.sources import TimedSource

class Random(TimedSource):
    def poll(self):
        randnum = random.random()
        self.push(randnum)
```

The configuration for a source of this module could look like this:

```yaml
workers:
  - Random:
    name: random-number
    interval: 10
```


## Why?

All network monitoring tools do 5min averages and render rrdtool PNGs and stuff like that. This does real-time data. On the other hand, you won't get long-term monitoring.

### Why Highcharts?

Other options, including d3, c3.js, chart.js, Flot, and a few others have been tested, but were either too complex, too slow, or had trouble with real-time updating line plots with multiple lines that get updated separately. Highcharts is pretty nifty, but the license sucks. It should be easy to replace Highcharts with something else in this project. Forks or pull-requests for more options on client-side frontends are welcome.

Other types of frontends (WebGL, steampunk-style gauges, ncurses, CLI, Android-App, ...?) would be awesome.

### Why python3?

If you're using debian oldstable and don't have up-to-date software available, try using a virtualenv, or some other distro. Python 3 has many improvements, e.g. much better multithreading supporti, asyncio, ipaddres, etc., which are important here, so get over it.

### Why websockets?

Websockets are cool. If your customers are using IE6 on Windows XP, you should think about getting new customers.


## Caveats

  * This is not a reliable monitoring system.
  * It won't give you long-term monitoring.
  * If you use the Highcharts frontend, be aware of the license.
  * SNMP interface counters can be inaccurate if they get updated only every few seconds.
