define(['knockout', 'lib/url'], function(ko, url) {

var ENTITIES = ['game', 'drive', 'play', 'play_player', 'player', 'aggregate'];

function QueryTable(controls, $node, start_entity) {
    var self = this;
    self.controls = controls;
    self.api = self.controls.api;
    self.$node = $node;
    self.rows = ko.observable(null);
    self.show_entities = ko.observableArray(ENTITIES);
    self.showing = ko.observable(start_entity || 'play');
    self.permalink = ko.observable(null);

    ko.applyBindings(self, self.$node[0]);

    self.update_rows(self.showing());
    self.controls.subscribe(function(val) {
        self.update_rows(self.showing());
    });
}

QueryTable.prototype.update_rows = function(entity) {
    var self = this;
    self.api.query(entity)
        .done(function(rows) {
            $('#nflfan-error').addClass('hidden');

            // This is probably a smell, but we get rid of the current
            // rows before switching the current entity so that Knockout
            // doesn't try to render something it can't handle.
            self.rows(null);
            self.showing(entity);
            self.rows(rows);

            var params = $.extend({}, self.api.params, {entity: self.showing()});
            delete params.refresh_count;
            var link = url.make(['query'], params);
            self.permalink(link);
            if (window.history && window.history.pushState) {
                window.history.pushState(params, '', link);
            }
        })
        .fail(function(jqXHR, textStatus) {
            $('#nflfan-error p').text(jqXHR.responseText);
            $('#nflfan-error').removeClass('hidden');
        });
};

QueryTable.prototype.show_as = function(entity) {
    var self = this;
    if (self.show_entities().indexOf(entity) == -1) {
        return;
    }
    self.update_rows(entity);
};

return QueryTable;
});
