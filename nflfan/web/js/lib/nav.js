define(['jquery', 'knockout', 'lib/rest'], function($, ko, API) {

function Weeks($node) {
    var self = this;
    this.api = new API();
    self.$node = $node;
    self.season = self.$node.data('season');
    self.phase = self.$node.data('phase');
    self.week = self.$node.data('week');

    self.seasons = ko.observable(null);
    self.phases = ko.observable(null);
    self.weeks = ko.observable(null);

    ko.applyBindings(self, self.$node[0]);

    self.api.weeks_phase(self.season, self.phase).done(function(weeks) {
        self.weeks(weeks);
    });
    self.api.seasons().done(function(seasons) {
        self.seasons(seasons);
    });
    self.api.phases(self.season).done(function(phases) {
        self.phases(phases);
    });
}

Weeks.prototype.url = function(params, val) {
    var cur = window.location.href;
    for (var i = 0; i < params.length; i++) {
        var reg = new RegExp(params[i]);
        if (reg.test(cur)) {
            return cur.replace(reg, '$1' + val);
        }
    }
};

$('.nflfan-weeks').each(function() { new Weeks($(this)); });
});
