define(['knockout'], function(ko) {

function Panel($node) {
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

Panel.prototype.subscribe = function(callback) {
    this.options.subscribe(callback);
};

return Panel;
});
