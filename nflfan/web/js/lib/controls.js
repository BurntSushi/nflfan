// If calling a method in the view with something like `$root.method`,
// then you'll need to use this instead:
//
//     function() { $root.method(...); }
//
// Where `$root` refers to an instance of `Panel`.
//
// It's a bug: https://github.com/knockout/knockout/issues/378
// (Well, not everyone thinks so, but it seems like a bug to me.)

define(['jq', 'knockout', 'lib/rest', 'lib/video'],
       function($, ko, API, Video) {

var DEFAULT_LIMITS = ['10', '20', '30', '40', '50', '100', '500'];
var ENTITIES = ['game', 'drive', 'play', 'play_player', 'player', 'aggregate'];
var OP_SUFFIX = {
    '=': '__eq', '!=': '__ne',
    '<': '__lt', '<=': '__le',
    '>': '__gt', '>=': '__ge'
};
var REFRESH_TIME = 10 * 1000;

function Panel($node, options) {
    var self = this;
    options = options || {};
    options.filters = options.filters || {};

    $node.submit(function() { return false; });
    $node.find('form').submit(function() { return false; });

    self.api = new API();
    self.video = new Video($('#video'));
    self.filters = {};
    self.options = options;
    self.available = $.extend({
        limits: DEFAULT_LIMITS,
        sort_entities: ENTITIES,
        search_entities: ENTITIES,
    }, self.options.available);
    for (k in self.available) {
        self.available[k] = ko.observableArray(self.available[k]);
    }
    self.my_players = ko.observable(self.options.my_players || false);
    self.refresh = ko.observable(false);
    self.refresh_int = null;
    self.refresh_count = ko.observable(0);

    self._init_entity_fields();
    self._init_limit();
    self._init_sort();
    self._init_search();

    // This is where the stuff in the UI is translated into URL parameters.
    // Not all changes in the UI correspond to a change in the URL parameters.
    // For example, adding a new selection box for an entity (no value and
    // no selected field).
    self.api_options = ko.computed(function() {
        var params = {
            // When the refresh count changes, it will force the parameters
            // to change. (If parameters don't change, then callbacks aren't
            // fired.)
            refresh_count: self.refresh_count(),
            refresh: self.refresh() ? '1' : '0',
            my_players: self.my_players() ? '1' : '0',
            limit: self.filters.limit(),
            sort:
                self.filters.sorts()
                    .filter(function(sortby) { return sortby.field(); })
                    .map(function(sortby) {
                        return sortby.order() + sortby.field();
                    })
        };
        self.filters.search().forEach(function(search) {
            var op = OP_SUFFIX[search.op()];
            if (!search.field() || !search.value() || !op) {
                return;
            }
            var key = search.entity() + '_' + search.field() + op;
            params[key] = search.value();
        });

        // If the parameters haven't changed, then return `null` indicating
        // that no new requests should be launched.
        // This isn't strictly necessary, but saves extra requests from being
        // made whenever a change in the UI doesn't translate to a change in
        // the query.
        if (params_equal(self.api.params, params)) {
            return null;
        } else {
            self.api.params = params;
            return params;
        }
    });

    self.refresh.subscribe(function(val) {
        if (val && self.refresh_int === null) {
            self.refresh_int = window.setInterval(
                function() {
                    // This will force the API parameters to change and all
                    // callbacks subscribed will be fired.
                    self.refresh_count(self.refresh_count() + 1);
                },
                REFRESH_TIME);
        } else if (!val && self._refresh_int !== null) {
            window.clearInterval(self.refresh_int);
            self.refresh_int = null;
        } else {
            console.log('Unknown refresh arguments. val: ' + val + ', ' +
                        'refresh_int: ' + self.refresh_int);
        }
    });
    self.refresh(self.options.refresh || false); // init the refresh

    ko.applyBindings(self, $node[0]);
}

Panel.prototype.watch_play = function(play) {
    var self = this;

    if (!play.video_url) {
        return;
    }
    self.video.watch(play.description, play.video_url);
};

Panel.prototype.subscribe = function(callback) {
    var self = this;
    self.api_options.subscribe(function(params) {
        if (params === null) {
            return;
        }
        callback(params);
    });
};

Panel.prototype.add_sort = function(entity) {
    if (this.available.sort_entities.indexOf(entity) == -1) {
        return;
    }
    this.filters.sorts.push({
        entity: ko.observable(entity),
        field: ko.observable(),
        order: ko.observable('-')
    });
};
Panel.prototype.remove_sort = function(field) {
    this.filters.sorts.remove(field);
};

Panel.prototype.add_search = function(entity) {
    if (this.available.search_entities().indexOf(entity) == -1) {
        return;
    }
    this.filters.search.push({
        entity: ko.observable(entity),
        field: ko.observable(),
        op: ko.observable('='),
        value: ko.observable()
    });
};
Panel.prototype.remove_search = function(field) {
    this.filters.search.remove(field);
};

Panel.prototype._init_entity_fields = function() {
    var self = this;

    self.entity_fields = {  // entity |--> [field]
        game: ko.observable(),
        drive: ko.observable(),
        play: ko.observable(),
        play_player: ko.observable(),
        aggregate: ko.observable(),
        player: ko.observable(),
        stats_play: ko.observable(),
        stats_play_player: ko.observable(),
    };
    self.api.fields().done(function(fields) {
        for (entity in fields) {
            self.entity_fields[entity](fields[entity]);
        }
    });
}

Panel.prototype._init_limit = function() {
    var self = this;
    self.filters.limit = ko.observable(self.options.filters.limit);
};

Panel.prototype._init_sort = function() {
    var self = this;

    self.filters.sorts = ko.observableArray();
    (self.options.filters.sorts || []).forEach(function(v) {
        self.filters.sorts.push({
            entity: ko.observable(v.entity),
            field: ko.observable(v.field),
            order: ko.observable(v.order)
        });
    });
};

Panel.prototype._init_search = function() {
    var self = this;

    self.filters.search = ko.observableArray();
    (self.options.filters.search || []).forEach(function(v) {
        self.filters.search.push({
            entity: ko.observable(v.entity),
            field: ko.observable(v.field),
            op: ko.observable(v.op),
            value: ko.observable(v.value)
        });
    });
};

// This tests whether two objects of type `string |--> (obj | string)` are 
// equivalent. This doesn't handle all corner cases but should be suitable
// for URL param objects.
function params_equal(p1, p2) {
    return is_subset(p1, p2) && is_subset(p2, p1);
}

function is_subset(p1, p2) {
    for (k in p1) {
        var t1 = typeof p1[k], t2 = typeof p2[k];
        if (t1 == 'undefined' || t2 == 'undefined') {
            if (t1 == t2) {
                // undefined really can't equal undefined, but it does here.
                continue;
            }
            return false;
        } else if (p1[k] == null || p2[k] == null) {
            if (p1[k] === p2) {
                continue;
            }
            return false;
        } else if (typeof p1[k] == 'object') {
            if (!params_equal(p1[k], p2[k])) {
                return false;
            }
        } else if (p1[k] != p2[k]) {
            return false;
        }
    }
    return true;
}

return Panel;

});
