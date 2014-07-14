define(['jquery', 'underscore.string'], function($, _s) {
function url(resource) {
    return _s.sprintf('/v1/%s', resource);
}

function game(gsis_id) {
    return $.getJSON(url(_s.sprintf('games/%s', gsis_id)));
}

function plays_week(season, phase, week) {
    return $.getJSON(url(_s.sprintf('seasons/%d/phases/%s/weeks/%d/plays',
                                    season, phase, week)));
}

function plays_game(gsis_id) {
    return $.getJSON(url(_s.sprintf('games/%s/plays', gsis_id)));
}

function seasons() { return $.getJSON(url('seasons')); }

function phases(season) {
    return $.getJSON(url(_s.sprintf('seasons/%d/phases', season)));
}

function weeks_phase(season, phase) {
    return $.getJSON(url(_s.sprintf('seasons/%d/phases/%s/weeks',
                                    season, phase)));
}

return {
    seasons: seasons,
    phases: phases,
    weeks_phase: weeks_phase,
    game: game,
    plays_week: plays_week,
    plays_game: plays_game,
}
});
