define(['jq', 'knockout', 'lib/rest'], function($, ko, API) {

function FanRoster($node) {
    var self = this;
    self.api = new API();
    self.$node = $node;
    self.league_name = $node.data('league-name');
    self.week = $node.data('week');

    self.owner_id = $node.data('owner-id');
    self.owner_name = $node.data('owner-name');
    self.opponent_id = $node.data('opponent-id');
    self.opponent_name = $node.data('opponent-name');

    self.show_bench = ko.observable(false);

    self.roster = ko.observable();
    self.total = ko.computed(function() {
        return roster_total_points(self.roster());
    });
    self.any_playing = ko.computed(function() {
        var roster = self.roster() || [];
        return roster.some(function(rp) {
            return rp.game && rp.game.is_playing;
        });
    });
    self.opponent_points = ko.observable(0);

    self.player_details = ko.observable();
    self.$node.popover({
        html: true,
        selector: '[rel="popover"]',
        trigger: 'focus'
    });

    self.update_roster();
    self.update_opponent_points();

    ko.applyBindings(self, self.$node[0]);
}

FanRoster.prototype.show_player_details = function(rplayer, ev) {
    var self = this;

    ev.preventDefault();
    if (!rplayer.player_id) {
        return;
    }
    var $el = $(ev.target);
    self.api
        .player_score_details(self.league_name, self.week, rplayer.player_id)
        .done(function(json) {
            self.player_details(json);
            var p = $el.data('bs.popover');
            p.options.content = self.$node.find('.popover-content').html();
            $el.popover('show');
            // This is necessary to prevent flickering with the animation
            // when the popover is shown the second, third, ... time.
            p.options.content = null;
        });
};

FanRoster.prototype.update_roster = function() {
    var self = this;
    self.api.scored_roster(self.league_name, self.week, self.owner_id)
        .done(function(json) {
            self.roster(json['players']);
        });
};

FanRoster.prototype.update_opponent_points = function() {
    var self = this;
    self.api.scored_roster(self.league_name, self.week, self.opponent_id)
        .done(function(json) {
            var pts = roster_total_points(json['players']);
            self.opponent_points(pts);
        });
};

function roster_total_points(roster) {
    roster = roster || [];
    return roster.filter(function(c) { return !c['bench']; })
                 .reduce(function(p, c) { return p + c['points']; }, 0);
}

return FanRoster;
});
