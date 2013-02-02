Highcharts.setOptions({
    global: {
        useUTC: false
    }
});



function ChartSeriesTarget(series) {
    this.series = series;
}
ChartSeriesTarget.prototype.add = function(time, value) {
    this.series.addPoint([time, value], false, false);
}
ChartSeriesTarget.prototype.populate = function(list) {
    this.series.setData(list);
}



function HtmlTarget(element, formatter) {
    this.element = element;
    this.formatter = formatter;
}
HtmlTarget.prototype.add = function(time, value) {
    if (this.formatter == undefined) {
        this.element.innerHtml = value;
    }
    else {
        this.element.innerHtml = formatter(value);
    }
}
HtmlTarget.prototype.populate = function(list) {
    keyvalue = list[list.length - 1];
    this.add(keyvalue[0], keyvalue[1]);
}



function Dashboard() {
    this.initCharts();
    this.fetchHistory();
}
Dashboard.prototype.initCharts = function() {
    CHARTS = {};
    targets = {};
    MAXVALUES = {};

    jQuery.getJSON('config.json', function(data) {
        var container = document.getElementById('container');

        for (var chartnum = 0; chartnum < data.charts.length; chartnum++) {
            var chart = data.charts[chartnum];
            var title = chart.name;

            var div = document.createElement('div');
            div.id = title;
            div.setAttribute("class", "chart");
            container.appendChild(div);

            var settings = {
                chart: {
                    renderTo: title, // div with id from title field
                    type: 'areaspline',
                    marginRight: 10
                },
                title: {
                    text: title
                },
                yAxis: {
                    title: {
                        text: chart.unit
                    }
                },
                series: []
            };
            if (chart.type == "integer") {
                settings.yAxis.allowDecimals = false;
            }

            var c = new Highcharts.Chart(settings);
            CHARTS[title] = c;

            for (var g = 0; g < chart.graphs.length; g++) {
                var graph = chart.graphs[g];

                var s = c.addSeries({
                    name: graph.name,
                    dataset: graph.dataset,
                    data: []
                });

                targets[graph.dataset] = new ChartSeriesTarget(s);
                MAXVALUES[graph.dataset] = chart.maxvalues;
            }
        }
        element = document.getElementById("loading_msg");
        element.parentNode.removeChild(element);
    });
}
Dashboard.prototype.fetchHistory = function() {

    // store local "this" for use in setInterval callback
    var t = this;

    jQuery.getJSON('/cgi-bin/history.json.py', function(data) {
        var interval = data.meta.interval;
        var lastrefresh = data.meta.refresh;
        for (var name in data.history) {
            var values = data.history[name].values;
            var length = values.length;
            var firstelement = 0;
            var maxvalues = MAXVALUES[name];
            if (length > maxvalues) {
                firstelement = length - maxvalues;
            }
            var points = [];
            for (var i = firstelement; i < length; i++) {
                var stepsbehind = i + 1 - length;
                var x = (lastrefresh + (interval * stepsbehind)) * 1000;
                points.push([x, values[i]]);
            }
            targets[name].populate(points);
        }
        for (var chartname in CHARTS) {
            CHARTS[chartname].redraw();
        }
        // set interval to update data every n seconds
        setInterval(function(){t.fetchUpdate();}, interval*1000);
    });
}
Dashboard.prototype.fetchUpdate = function() {
    jQuery.getJSON('/cgi-bin/latest.json.py', function(data) {
        var lastrefresh = data.meta.refresh;
        for (var name in data.latest) {
            var set = data.latest[name];
            targets[name].add(lastrefresh*1000, set.value);
        }
        for (var chartname in CHARTS) {
            CHARTS[chartname].redraw();
        }
    });
}

