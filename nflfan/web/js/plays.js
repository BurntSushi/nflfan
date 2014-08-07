require(['jquery', 'lib/controls', 'lib/play-table', 'lib/url', 'lib/nav', 'bootstrap'],
        function($, PanelControls, PlayTable, url) {

$(document).ready(function() {
    var ENTITIES = ['game', 'drive', 'play', 'play_player', 'player', 'aggregate'];
    var OPS = {'eq': '=', 'ne': '!=', 'gt': '>', 'ge': '>=', 'lt': '<', 'le': '<='};

    var params = url.params(window.location.href);
    var limit = undefined, search = [], sorts = [];
    for (param in params) {
        if (param == 'sort') {
            var fields = params[param];
            if (typeof fields == 'string') {
                fields = [fields];
            }
            fields.forEach(function(field) {
                sorts.push({
                    entity: 'play',
                    field: field.substr(1),
                    order: field[0]
                });
            });
            continue;
        }
        if (param == 'limit') {
            limit = params[param];
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
        available: { }, // everything is available
        filters: {
            limit: limit,
            search: search,
            sorts: sorts
        }
    });
    $('.nflfan-play-table').each(function() {
        new PlayTable($controls, $(this));
    });
});

});
