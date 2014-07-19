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

    // Ug. Apparently KO does not set `this` correct when using special
    // bindings like `$parent` or `$root`. Therefore, we've got to define
    // this method in the constructor so we can close over `self`.
    self.remove_sort_field = function(field) {
        self.filters.sorts.remove(field);
    };

    ko.applyBindings(self, self.$node[0]);
}

Panel.prototype.subscribe = function(callback) {
    this.options.subscribe(callback);
};

Panel.prototype.add_sort_field = function() {
    this.filters.sorts.push({
        field: ko.observable(),
        order: ko.observable('+')
    });
};

return Panel;

});
