function formatData(value, suffix) {
    var i = 0;
    while (value >= 1000) {
        i++;
        value /= 1000;
    }
    return value.toPrecision(3) + " " + ["", "k", "M", "G", "T", "E"][i] + suffix;
}



function ChartSeriesTarget(series, maxvalues) {
    this.series = series;
    this.maxvalues = maxvalues;
}
ChartSeriesTarget.prototype.add = function(time, value) {
    // shift chart if maximum number of values is already stored
    var shift = (this.series.data.length >= this.maxvalues);
    this.series.addPoint([time, value], false, shift);
}
ChartSeriesTarget.prototype.populate = function(list) {
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
    this.charts = {};
    this.targets = []; // list of key/value pairs
    this.updateInterval = 10; // default value
}
Dashboard.prototype.addTarget = function(source, target) {
    // data from source dataset gets added to the target
    if (!this.targets[source]) {
        this.targets[source] = [];
    }
    this.targets[source].push(target);
}
Dashboard.prototype.fetchHistory = function() {
    // store dashboard context
    var t = this;

    jQuery.getJSON('/cgi-bin/history.json.py', function(data) {
        var interval = data.meta.interval;
        t.updateInterval = interval;
        var lastrefresh = data.meta.refresh;
        for (var name in data.history) {
            for (var tnum in t.targets[name]) {
                var target = t.targets[name][tnum];
                var values = data.history[name].values;
                var length = values.length;
                var firstelement = 0;
                var maxvalues = target.maxvalues;
                if (length > maxvalues) {
                    firstelement = length - maxvalues;
                }
                var points = [];
                for (var i = firstelement; i < length; i++) {
                    var stepsbehind = i + 1 - length;
                    var x = (lastrefresh + (interval * stepsbehind)) * 1000;
                    points.push([x, values[i]]);
                }
                target.populate(points);
            }
        }
        for (var chartname in t.charts) {
            t.charts[chartname].redraw();
        }
    });
}
Dashboard.prototype.fetchUpdate = function() {
    // store dashboard context
    var t = this;

    jQuery.getJSON('/cgi-bin/latest.json.py', function(data) {
        var lastrefresh = data.meta.refresh;
        for (var name in data.latest) {
            for (var tnum in t.targets[name]) {
                var target = t.targets[name][tnum];
                var set = data.latest[name];
                target.add(lastrefresh*1000, set.value);
            }
        }
        for (var chartname in t.charts) {
            t.charts[chartname].redraw();
        }
    });
}
Dashboard.prototype.scheduleUpdates = function() {
    // set interval to update data every n seconds
    var t = this;
    setInterval(function(){t.fetchUpdate();}, t.updateInterval*1000);
}
Dashboard.prototype.addChart = function(chart, title) {
    this.charts[title] = chart;
}
Dashboard.prototype.getChartByName = function(name) {
    return this.charts[name];
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
