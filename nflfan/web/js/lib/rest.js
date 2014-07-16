define(['jquery', 'sprintf'], function($, Sprintf) {
console.log(Sprintf);
var sprintf = Sprintf.sprintf;

function url(resource) {
    return sprintf('/v1/%s', resource);
}

function game(gsis_id) {
    var convert_date = function(json) {
        json.start_time = new Date(json.start_time);
    };
    return $.getJSON(url(sprintf('games/%s', gsis_id))).done(convert_date);
}

function plays_week(season, phase, week) {
    return $.getJSON(url(sprintf('seasons/%d/phases/%s/weeks/%d/plays',
                                 season, phase, week)));
}

function plays_game(gsis_id) {
    return $.getJSON(url(sprintf('games/%s/plays', gsis_id)));
}

function seasons() { return $.getJSON(url('seasons')); }

function phases(season) {
    return $.getJSON(url(sprintf('seasons/%d/phases', season)));
}

function weeks_phase(season, phase) {
    return $.getJSON(url(sprintf('seasons/%d/phases/%s/weeks',
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
