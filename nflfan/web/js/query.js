require(['jq', 'lib/controls', 'lib/query', 'lib/url', 'lib/nav',
         'lib/error', 'bootstrap'],
        function($, PanelControls, QueryTable, url) {

$(document).ready(function() {
    var ENTITIES = ['game', 'drive', 'play', 'play_player', 'player', 'aggregate'];
    var OPS = {'eq': '=', 'ne': '!=', 'gt': '>', 'ge': '>=', 'lt': '<', 'le': '<='};

    var params = url.params(window.location.href);
    var search = [], sorts = [];
    var simple_params = {
        limit: 50,
        entity: 'play',
        my_players: false,
        refresh: false,
    }
    for (param in params) {
        if (typeof simple_params[param] != 'undefined') {
            simple_params[param] = params[param];
        }
    }
    for (param in params) {
        if (typeof simple_params[param] != 'undefined') {
            continue;
        }
        if (param == 'sort') {
            var fields = params[param];
            if (typeof fields == 'string') {
                fields = [fields];
            }
            fields.forEach(function(field) {
                sorts.push({
                    entity: simple_params.entity,
                    field: field.substr(1),
                    order: field[0]
                });
            });
            continue;
        }

        var found = false;
        for (var i = 0; i < ENTITIES.length; i++) {
            if (param.substr(0, ENTITIES[i].length+1) == (ENTITIES[i] + '_')) {
                found = true;
                var pieces = param.substr(ENTITIES[i].length+1).split('__');
                var field = pieces[0], op = OPS[pieces[1] || 'eq'];
                search.push({
                    entity: ENTITIES[i],
                    field: field,
                    op: op,
                    value: params[param]
                });
            }
        }
        if (!found) {
            console.log('WARNING: Invalid parameter prefix in ' + param);
        }
    }
    var $controls = new PanelControls($('#nflfan-panel-controls'), {
        my_players: simple_params.my_players == '1',
        refresh: simple_params.refresh == '1',
        available: { }, // everything is available
        filters: {
            limit: simple_params.limit,
            search: search,
            sorts: sorts
        }
    });
    $('.nflfan-query-table').each(function() {
        new QueryTable($controls, $(this), simple_params.entity);
    });
});

});
