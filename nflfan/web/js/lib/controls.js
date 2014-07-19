define(['knockout', 'lib/rest'], function(ko, API) {

function Panel($node) {
    var self = this;
    self.api = new API();
    self.$node = $node;
    self.filters = {
        limit: ko.observable(undefined),
        sorts: ko.observableArray([{
            field: ko.observable(), order: ko.observable('+')
        }])
    };
    self.available = {
        limits: ['10', '20', '30', '40', '50', '100'],
        fields: ['down', 'points']
    }
    self.options = ko.computed(function() {
        var params = {
            limit: self.filters.limit(),
            sort:
                self.filters.sorts()
                    .filter(function(sortby) {
                        return typeof sortby.field() !== 'undefined';
                    })
                    .map(function(sortby) {
                        return sortby.order() + sortby.field();
                    })
        };
        self.api.params = params;
        return params;
    });


    ko.applyBindings(self, self.$node[0]);
}

Panel.prototype.subscribe = function(callback) {
    this.options.subscribe(callback);
};

Panel.prototype.add_sort = function() {
    this.filters.sorts.push({
        field: ko.observable(),
        order: ko.observable('+')
    });
};

// If calling this in the view with something like `$root.remove_sort`,
// then you'll need to use this instead:
//
//     function() { $root.remove_sort(...); }
//
// It's a bug: https://github.com/knockout/knockout/issues/378
// (Well, not everyone thinks so, but it seems like a bug to me.)
Panel.prototype.remove_sort = function(field) {
    this.filters.sorts.remove(field);
};

return Panel;

});
