define(['knockout'], function(ko) {

var PLAYING_REFRESH_TIME = 10;
var NOT_STARTED_REFRESH_TIME = 60;

function GamePanel(controls, $node) {
    var self = this;
    self.controls = controls;
    self.api = self.controls.api;
    self.$node = $node;
    self.gsis_id = $node.data('gsis-id');
    self.game = ko.observable(null);
    self.plays = ko.observable(null);

    ko.applyBindings(self, self.$node[0]);

    self.update_game();
    self.update_plays();
    self.controls.subscribe(function(val) {
        self.update_plays();
    });
}

GamePanel.prototype.update_game = function() {
    var self = this;
    self.api.game(self.gsis_id).done(function(game) {
        self.game(game);
        if (!game.finished) {
            var t;
            if (game.is_playing) {
                t = PLAYING_REFRESH_TIME;
            } else {
                t = NOT_STARTED_REFRESH_TIME;
            }
            // We reset the timeout each time because the interval may change
            // depending on whether the game is playing or not.
            window.setTimeout(
                function() { self.update_game(); self.update_plays(); },
                random_refresh_interval(t));
        }
    });
};

GamePanel.prototype.update_plays = function() {
    var self = this;
    self.api.plays_game(self.gsis_id).done(function(plays) {
        self.plays(plays);
    });
}

GamePanel.prototype.nice_start_time = function() {
    return nice_datetime(this.game().start_time);
};

function random_refresh_interval(middle) {
    var min = middle - 3;
    var max = middle + 3;
    return 1000 * (Math.floor(Math.random() * (max - min)) + min);
}

return GamePanel;
});
