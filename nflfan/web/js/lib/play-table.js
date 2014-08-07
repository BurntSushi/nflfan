define(['knockout'], function(ko) {

function PlayTable(controls, $node) {
    var self = this;
    self.controls = controls;
    self.api = self.controls.api;
    self.$node = $node;
    self.plays = ko.observable(null);

    ko.applyBindings(self, self.$node[0]);

    self.update_plays();
    self.controls.subscribe(function(val) {
        self.update_plays();
    });
}

PlayTable.prototype.update_plays = function() {
    var self = this;
    self.api.plays().done(function(plays) {
        self.plays(plays);
    });
}

return PlayTable;
});
