define(['jquery', 'knockout', 'lib/rest'], function($, ko, API) {

var DEFAULT_LIMITS = ['10', '20', '30', '40', '50', '100'];
var DEFAULT_SORT_FIELDS = ['Game', 'Drive', 'Play', 'PlayPlayer', 'Player'];

function Panel($node, options) {
    var self = this;
    options = options || {};
    options.filters = options.filters || {};

    self.api = new API();
    self.filters = {};
    self.available = $.extend({
        limits: DEFAULT_LIMITS,
        sort_fields: DEFAULT_SORT_FIELDS
    }, options.available);

    self._init_limit(options);
    self._init_sort(options);

    self.api_options = ko.computed(function() {
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

    ko.applyBindings(self, $node[0]);
}

Panel.prototype._init_limit = function(options) {
    var self = this;

    self.filters.limit = ko.observable(options.filters.limit);
};

Panel.prototype._init_sort = function(options) {
    var self = this;

    var sorts = options.filters.sorts || [{field: undefined, order: '+'}];
    self.filters.sorts = ko.observableArray();
    sorts.forEach(function(v) {
        self.filters.sorts.push({
            field: ko.observable(v.field),
            order: ko.observable(v.order)
        });
    });

    self.sort_fields = ko.observableArray();
    self.available.sort_fields.forEach(function(entity) {
        self.api.fields(entity).done(function(fields) {
            self.sort_fields.push({entity: entity, fields: fields});
            self.sort_fields.sort(function(a, b) {
                return a.entity < b.entity ? -1 : 1;
            });
        });
    });
};

Panel.prototype.subscribe = function(callback) {
    this.api_options.subscribe(callback);
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
