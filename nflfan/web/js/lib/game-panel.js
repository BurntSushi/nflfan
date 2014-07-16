define(['knockout', 'rest'], function(ko, rest) {

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

    rest.game(self.gsis_id).done(function(game) {
        self.game(game);
    });
    rest.plays_game(self.gsis_id).done(function(plays) {
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

return GamePanel;
});
