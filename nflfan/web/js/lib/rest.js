define(['jquery', 'lib/url'], function($, url) {
function API(params) {
    this.params = params || {};
}

// Returns a URL for the corresponding API request.
// See `lib/url.make` for documentation.
// Note that this does not take `params` since those are constructed
// independently.
API.prototype.url = function(pieces) {
    return url.make(['v1'].concat(pieces), this.params);
};

API.prototype.game = function(gsis_id) {
    var convert_date = function(json) {
        json.start_time = new Date(json.start_time);
    };
    return $.getJSON(this.url(['games', gsis_id])).done(convert_date);
};

API.prototype.plays_week = function(season, phase, week) {
    var path = ['seasons', season, 'phases', phase, 'weeks', week, 'plays'];
    return $.getJSON(this.url(path));
};

API.prototype.plays_game = function(gsis_id) {
    return $.getJSON(this.url(['games', gsis_id, 'plays']));
};

API.prototype.seasons = function () {
    return $.getJSON(this.url(['seasons']));
};

API.prototype.phases = function(season) {
    return $.getJSON(this.url(['seasons', season, 'phases']));
};

API.prototype.weeks_phase = function(season, phase) {
    var path = ['seasons', season, 'phases', phase, 'weeks'];
    return $.getJSON(this.url(path));
};

return API;
});
