define(['knockout'], function(ko) {

function PlayTable(controls, $node) {
    var self = this;
    self.controls = controls;
    self.api = self.controls.api;
    self.$node = $node;
    self.rows = ko.observable(null);

    ko.applyBindings(self, self.$node[0]);

    self.update_rows();
    self.controls.subscribe(function(val) {
        self.update_rows();
    });
}

PlayTable.prototype.update_rows = function() {
    var self = this;
    self.api.query('play').done(function(rows) {
        self.rows(rows);
    });
}

return PlayTable;
});
