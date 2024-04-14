function formatData(value, suffix) {
    if (value == null) return "";
    var i = 0;
    while (Math.round(value) >= 1000) {
        i++;
        value /= 1000;
    }
    return parseFloat(value).toPrecision(3) + " " + ["", "k", "M", "G", "T", "P", "E"][i] + suffix;
}



function ChartSeriesTarget(series, maxvalues) {
    this.series = series;
    this.maxvalues = maxvalues;
}
ChartSeriesTarget.prototype.add = function(time, value) {
    // shift chart if maximum number of values is already stored
    var shift = (this.series.data.length >= this.maxvalues);
    this.series.addPoint([time*1000, parseFloat(value)], false, shift);
}
ChartSeriesTarget.prototype.populate = function(list) {
    // convert normal timestamps to stupid javascript timestamps
    for (var i = 0; i < list.length; i++) {
        list[i][0] = 1000 * list[i][0]
    }

    list = list.splice(-this.maxvalues);
    this.series.setData(list);
}



function HtmlTarget(element, formatter) {
    if (typeof(element) == "string") {
        element = document.getElementById(element);
    }
    this.element = element;
    this.maxvalues = 1;
    this.formatter = formatter;
}
HtmlTarget.prototype.add = function(time, value) {
    if (this.formatter == undefined) {
        this.element.innerHTML = value;
    }
    else {
        this.element.innerHTML = this.formatter(value);
    }
}
HtmlTarget.prototype.populate = function(list) {
    keyvalue = list[list.length - 1];
    this.add(keyvalue[0], keyvalue[1]);
}



function Dashboard() {
    this.chart_by_name = {};
    this.charts = [];
    this.targets = []; // list of key/value pairs
    this.updateInterval = 10; // default value
    this.redrawScheduled = false;
    this.url = "";
}
Dashboard.prototype.addTarget = function(source, target) {
    // data from source dataset gets added to the target
    if (!this.targets[source]) {
        this.targets[source] = [];
    }
    this.targets[source].push(target);
}
Dashboard.prototype.requestRedraws = function(ms) {
    if (this.redrawScheduled == false) {
        this.redrawScheduled = true;
        var t = this;
        setTimeout(function() { t.redrawCharts(); }, ms);
    }
}
Dashboard.prototype.redrawCharts = function() {
    for (var i in this.charts) {
        this.charts[i].redraw();
    }
    this.redrawScheduled = false;
}
Dashboard.prototype.onUpdate = function(channel, timestamp, value) {
    for (var i = 0; i < this.targets[channel].length; i++) {
        var target = this.targets[channel][i];
        target.add(timestamp, value);
    }
}
Dashboard.prototype.populate = function(channel, timeseries) {
    for (var i = 0; i < this.targets[channel].length; i++) {
        var target = this.targets[channel][i];
        target.populate(timeseries);
    }
}
Dashboard.prototype.subscribe = function() {
    var channels = Object.keys(this.targets);
    var data = JSON.stringify({
        message:"subscribe",
        data: channels
    });
    this.ws.send(data);
}
Dashboard.prototype.getHistory = function() {
    var channels = Object.keys(this.targets);
    var data = JSON.stringify({
        message:"history",
        data: channels
    });
    this.ws.send(data);
}
Dashboard.prototype.checkWebsocket = function() {
    var t = this;
    if (this.ws.readyState > 1) {
        // recover from closed websocket
        this.start()
    } else if (this.lastUpdate < (Date.now() - 5*60*1000)) {
        // recover from a probably broken connection (websocket hasn't given up yet)
        this.start();
    } else {
        setTimeout(function(){t.checkWebsocket();}, 10000);
    }
}
Dashboard.prototype.start = function() {
    // set interval to update data every n seconds
    var t = this;

    if (this.hasOwnProperty("ws")) {
        this.ws.close();
    }

    this.ws = new WebSocket(this.url);
    this.lastUpdate = Date.now();
    this.ws.onopen = function() {
        t.getHistory();
        t.subscribe();
    };
    this.ws.onerror = function() {
        t.ws.close();
    };
    this.ws.onmessage = function (evt) {
        var data = JSON.parse(evt.data);
        if (data.message == "update") {
            t.lastUpdate = Date.now();
            var updates = data.data;
            for (channel in updates) {
                var timestamp = Object.keys(updates[channel])[0];
                var value = updates[channel][timestamp];
                t.onUpdate(channel, timestamp, value);
            }
            t.requestRedraws(200);
        } else if (data.message == "history") {
            // push history to targets
            var updates = data.data;
            for (channel in updates) {
                var timeseries = updates[channel];
                if (timeseries.length > 0) 
                    t.populate(channel, timeseries);
            }

            // trigger a frefresh for all targets
            t.requestRedraws(200);
        };
    };
    this.checkWebsocket();
}
Dashboard.prototype.addChart = function(chart, title) {
    this.chart_by_name[title] = chart;
    this.charts.push(chart);
}
Dashboard.prototype.getChartByName = function(name) {
    return this.chart_by_name[name];
}
Dashboard.prototype.getTargetsByDatasetName = function(name) {
    return this.targets[name];
}
Dashboard.prototype.createChart = function(container, title, ylabel, flags) {
    if (typeof(container) == "string") {
        container = document.getElementById(container);
    }
    var settings = {
        chart: {
            renderTo: container,
            type: "line",
            zoomType: "x",
            marginRight: 10
        },
        title: {
            text: title
        },
        yAxis: {
            title: {
                text: ylabel
            }
        },
        series: []
    };
    var flag;
    for (var i = 0; i < flags.length; i++) {
        flag = flags[i];
        if (flag == "integer") {
            settings.yAxis.allowDecimals = false;
        }
        else if (flag == "zero") {
            settings.yAxis.min = 0;
        }
    }

    var chart = new Highcharts.Chart(settings);
    this.addChart(chart, title);
    return chart;
}
Dashboard.prototype.addSeriesToChart = function(chart, title, dataset, maxvalues) {
    if (typeof(chart) == "string") {
        chart = this.getChartByName(chart);
    }

    var series = chart.addSeries({
        name: title,
        data: []
    });
    this.addTarget(dataset, new ChartSeriesTarget(series, maxvalues));
    return series;
}

