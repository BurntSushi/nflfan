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

API.prototype.json = function(url_pieces) {
    return $.getJSON(this.url(url_pieces));
}

API.prototype.game = function(gsis_id) {
    var convert_date = function(json) {
        json.start_time = new Date(json.start_time);
    };
    return this.json(['games', gsis_id]).done(convert_date);
};

API.prototype.plays = function() {
    return this.json(['plays']);
};

API.prototype.plays_week = function(season, phase, week) {
    return this.json(['seasons', season, 'phases', phase,
                      'weeks', week, 'plays']);
};

API.prototype.plays_game = function(gsis_id) {
    return this.json(['games', gsis_id, 'plays']);
};

API.prototype.seasons = function () {
    return this.json(['seasons']);
};

API.prototype.phases = function(season) {
    return this.json(['seasons', season, 'phases']);
};

API.prototype.weeks_phase = function(season, phase) {
    return this.json(['seasons', season, 'phases', phase, 'weeks']);
};

API.prototype.fields = function(entity) {
    return this.json(['fields', entity]);
};

API.prototype.roster = function(lg_name, week, owner) {
    return this.json(['leagues', lg_name, 'weeks', week, 'rosters', owner]);
};

API.prototype.scored_roster = function(lg_name, week, owner) {
    var old = this.params;
    this.params = { 'scored': '1' };
    var r = this.json(['leagues', lg_name, 'weeks', week, 'rosters', owner]);
    this.params = old;
    return r;
};

API.prototype.player_score_details = function(lg_name, week, player_id) {
    return this.json(['leagues', lg_name, 'weeks', week, 'players', player_id]);
};

return API;
});
