require(['jquery', 'lib/controls', 'lib/game-panel', 'lib/nav', 'bootstrap'],
        function($, PanelControls, GamePanel) {

// Some breadcrumbs:
//
// 1) I need a good story about passing sorting/limiting options to REST
//    requests. Idea: figure out how to use the special `arguments` variable
//    and accept simple option dictionaries.
//    e.g., {'limit': 25, 'sort': ['+time', '-yards_to_go']} would map to
//    the obvious REST query params.
// 2) We need a widget for sorting controls. This would normally be too complex
//    for me to even consider, but I think Knockout will make it simple. Yay.
// 3) PanelControls + GamePanel is a thing.
//    Weeks is a thing.
//    Sort panel will be a thing.
//    Roster panel will be a thing.
// 4) Perhaps Roster will be a list of RosterPlayer, where RosterPlayer is
//    also a thing.
// 5) Figure out how to integrate league info into everything.
//    We know how to get roster info for a week. We can use that to tie
//    into plays (which contain player ids).
//    How to display? Colors? Would like colors for types of plays though.
//    Hmm.

$(document).ready(function() {
    var $controls = new PanelControls($('#nflfan-panel-controls'), {
        available: {
            sort_entities: ['play'],
            search_entities: ['player', 'drive', 'play', 'play_player']
        },
        filters: {
            sorts: [{entity: 'play', field: 'play_id', order: '-'}],
        }
    });
    $('.nflfan-panel-game').each(function() {
        new GamePanel($controls, $(this));
    });
});

});
