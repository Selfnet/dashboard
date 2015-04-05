function Dashboard() {
    this.targets = {};
    this.next_target_id = 0;
}
Dashboard.prototype.addTarget = function(channel, callback) {
    if (!(channel in this.targets)) this.targets[channel] = [];
    var id = this.next_target_id++;
    this.targets[channel].push({
        id: id,
        callback: callback,
    });
    return id;
}
Dashboard.prototype.removeTarget = function(id) {
    for (key in this.targets) {
        this.targets[key] = this.targets[key].filter(function(target) {
            return target.id !== id;
        });
    }
    // TODO unsubscribe channels?
}
Dashboard.prototype.addChart = function(settings) {
    var cc = new ChartConnector(settings);
    var channels = settings.channels;
    var callbackIDs = [];
    for (name in channels) {
        var channel = channels[name];
        var cid = this.addTarget(channel, cc.onUpdate.bind(cc));
        callbackIDs.push(cid);
    }
    return callbackIDs;
}
Dashboard.prototype.onUpdate = function(channel, timestamp, value) {
    for (var i = 0; i < this.targets[channel].length; i++) {
        var target = this.targets[channel][i];
        target.callback(channel, timestamp, value);
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
Dashboard.prototype.run = function(url) {
    // TODO check if still connected and maybe disconnect first

    // context
    var t = this;

    this.ws = new WebSocket(url);
    this.ws.onopen = function() {
        t.subscribe();
    };
    this.ws.onerror = function() {
        t.ws.close();
    };
    this.ws.onmessage = function (evt) {
        var data = JSON.parse(evt.data);
        if (data.message == "update") {
            var updates = data.data;
            for (channel in updates) {
                var timestamp = Object.keys(updates[channel])[0];
                var value = updates[channel][timestamp];
                t.onUpdate(channel, timestamp, value);
            };
        };
    };
}

function ChartConnector(settings) {
    this.settings = settings;
    this.timestamps = {};
    this.values = {};
}
ChartConnector.prototype.onUpdate = function(channel, timestamp, value) {
    if (!(channel in this.timestamps)) this.timestamps[channel] = [];
    if (!(channel in this.values)) this.values[channel] = [];
    // javascript uses milliseconds for timestamps
    var timestamp = Math.floor(timestamp*1000);
    this.timestamps[channel].push(timestamp);
    this.values[channel].push(value);

    if ("length" in this.settings) {
        // leave the last N values
        var slice = -this.settings.length;
    } else {
        // remove the first value
        var slice = 1;
    }
    this.timestamps[channel] = this.timestamps[channel].slice(slice);
    this.values[channel] = this.values[channel].slice(slice);

    this.updateChart();
}
ChartConnector.prototype.updateChart = function() {
    var channels = this.settings.channels;
    var columns = [];
    for (name in channels) {
        var channel = channels[name];
        columns.push([].concat(name + "-ts", this.timestamps[channel]));
        columns.push([].concat(name, this.values[channel]));
    }
    this.settings.chart.load({
        columns: columns
    });
}
