define(['knockout'], function(ko) {

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

return GamePanel;
});
