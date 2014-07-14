require(['jquery', 'underscore.string', 'knockout', 'nflfan-rest',
         'text!ko/game-panel.html', 'text!ko/weeks.html', 'bootstrap'],
        function($, _s, ko, fan, html_panel, html_weeks) {
function GamePanel($node) {
    var self = this;
    self.$node = $node;
    self.gsis_id = $node.data('gsis-id');
    self.game = ko.observable(null);
    self.plays = ko.observable(null);

    self.$node.html(html_panel);
    ko.applyBindings(self, self.$node[0]);

    fan.game(self.gsis_id).done(function(game) {
        self.game(game);
    });
    fan.plays_game(self.gsis_id).done(function(plays) {
        self.plays(plays);
    });
}

function Weeks($node) {
    var self = this;
    self.$node = $node;
    self.season = self.$node.data('season');
    self.phase = self.$node.data('phase');
    self.week = self.$node.data('week');

    self.seasons = ko.observable(null);
    self.phases = ko.observable(null);
    self.weeks = ko.observable(null);

    self.$node.html(html_weeks);
    ko.applyBindings(self, self.$node[0]);

    fan.weeks_phase(self.season, self.phase).done(function(weeks) {
        self.weeks(weeks);
    });
    fan.seasons().done(function(seasons) {
        self.seasons(seasons);
    });
    fan.phases(self.season).done(function(phases) {
        self.phases(phases);
    });
}

Weeks.prototype.url = function(param, val) {
    var reg = new RegExp(param + "/[^/]+");
    return window.location.href.replace(reg, param + '/' + val);
};

$(document).ready(function() {
    $('.nflfan-weeks').each(function() { new Weeks($(this)); });
    $('.nflfan-panel-game').each(function() { new GamePanel($(this)); });
});
});
