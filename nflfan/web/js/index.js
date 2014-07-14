require(['jquery', 'underscore.string', 'knockout', 'nflfan-rest',
         'text!ko/weeks.html', 'bootstrap'],
        function($, _s, ko, fan, html_weeks) {

// Some breadcrumbs:
//
// 1) I need a good story about passing sorting/limiting options to REST
//    requests. Idea: figure out how to use the special `arguments` variable
//    and accept simple option dictionaries.
//    e.g., {'limit': 25, 'sort': ['+time', '-yards_to_go']} would map to
//    the obvious REST query params.
// 2) We need a widget for sorting controls. This would normally be too complex
//    for me to even consider, but I think Knockout will make it simple. Yay.
// 3) PanelControls + GamePanel is a thing.
//    Weeks is a thing.
//    Sort panel will be a thing.
//    Roster panel will be a thing.
// 4) Perhaps Roster will be a list of RosterPlayer, where RosterPlayer is
//    also a thing.
// 5) Figure out how to integrate league info into everything.
//    We know how to get roster info for a week. We can use that to tie
//    into plays (which contain player ids).
//    How to display? Colors? Would like colors for types of plays though.
//    Hmm.
// 6) Get rid of text!blah.html dependencies. Just use Bottle templates.
//    There's no real reason not to.
// 7) Get rid of underscore and underscore.string dependency. I think I can
//    (or WANT) to make due without them.
//    However, find a good sprintf.
//    This looks promising: https://github.com/alexei/sprintf.js

function PanelControls($node) {
    var self = this;
    self.$node = $node;
    self.limit = ko.observable('30');
    self.limits = ['10', '20', '30', '40', '50', '100'];
    self.options = ko.computed(function() {
        return {
            limit: self.limit()
        }
    });

    ko.applyBindings(self, self.$node[0]);
}

PanelControls.prototype.subscribe = function(callback) {
    this.options.subscribe(callback);
};

function GamePanel(controls, $node) {
    var self = this;
    self.controls = controls;
    self.$node = $node;
    self.gsis_id = $node.data('gsis-id');
    self.game = ko.observable(null);
    self.plays = ko.observable(null);

    ko.applyBindings(self, self.$node[0]);

    self.controls.subscribe(function(val) {
        console.log('GamePanel: ' + val.limit);
    });

    fan.game(self.gsis_id).done(function(game) {
        self.game(game);
    });
    fan.plays_game(self.gsis_id).done(function(plays) {
        self.plays(plays);
    });
}

GamePanel.prototype.nice_start_time = function() {
    var options = {
        hour12: true,
        weekday: 'short',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    };
    return this.game().start_time.toLocaleDateString(undefined, options);
};

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
    var $controls = new PanelControls($('#nflfan-panel-game-controls'));
    $('.nflfan-weeks').each(function() { new Weeks($(this)); });
    $('.nflfan-panel-game').each(function() {
        new GamePanel($controls, $(this));
    });
});
});
