Highcharts.setOptions({
    global: {
        useUTC: false
    }
});



function initCharts() {
    CHARTS = {};
    SERIES = {};
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
            var c = new Highcharts.Chart(settings);
            CHARTS[title] = c;

            for (var g = 0; g < chart.graphs.length; g++) {
                var graph = chart.graphs[g];

                var s = c.addSeries({
                    name: graph.name,
                    dataset: graph.dataset,
                    data: []
                });

                SERIES[graph.dataset] = s;
                MAXVALUES[graph.dataset] = chart.maxvalues;
            }
        }
        element = document.getElementById("loading_msg");
        element.parentNode.removeChild(element);
    });
}

function fetchHistory() {
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
            for (var i = firstelement; i < length; i++) {
                var stepsbehind = i + 1 - length;
                var x = (lastrefresh + (interval * stepsbehind)) * 1000;
                SERIES[name].addPoint([x, values[i]], false, false);
            }
        }
        for (var chartname in CHARTS) {
            CHARTS[chartname].redraw();
        }
        setInterval("fetchUpdate()", interval*1000);
    });
}

function fetchUpdate() {
    jQuery.getJSON('/cgi-bin/latest.json.py', function(data) {
        var lastrefresh = data.meta.refresh;
        for (var name in data.latest) {
            var set = data.latest[name];
            SERIES[name].addPoint([lastrefresh*1000, set.value], false, true);
        }
        for (var chartname in CHARTS) {
            CHARTS[chartname].redraw();
        }
    });
}

function init() {
    initCharts();
    fetchHistory();
}

init();

