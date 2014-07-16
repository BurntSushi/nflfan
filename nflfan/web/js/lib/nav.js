define(['jquery', 'knockout', 'lib/rest'], function($, ko, rest) {

function Weeks($node) {
    var self = this;
    self.$node = $node;
    self.season = self.$node.data('season');
    self.phase = self.$node.data('phase');
    self.week = self.$node.data('week');

    self.seasons = ko.observable(null);
    self.phases = ko.observable(null);
    self.weeks = ko.observable(null);

    ko.applyBindings(self, self.$node[0]);

    rest.weeks_phase(self.season, self.phase).done(function(weeks) {
        self.weeks(weeks);
    });
    rest.seasons().done(function(seasons) {
        self.seasons(seasons);
    });
    rest.phases(self.season).done(function(phases) {
        self.phases(phases);
    });
}

Weeks.prototype.url = function(param, val) {
    var reg = new RegExp(param + "/[^/]+");
    return window.location.href.replace(reg, param + '/' + val);
};

$('.nflfan-weeks').each(function() { new Weeks($(this)); });

});
