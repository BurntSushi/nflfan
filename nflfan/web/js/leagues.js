require(['jquery', 'lib/fan-roster', 'lib/nav', 'bootstrap'],
        function($, FanRoster) {

$(document).ready(function() {
    var rosters = [];
    $('.nflfan-panel-fanroster').each(function() {
        rosters.push(new FanRoster($(this)));
    });

    var text_show = 'Show benches', text_hide = 'Hide benches';
    $('#bench-toggle').text(text_show);
    $('#bench-toggle').click(function(ev) {
        ev.preventDefault();
        var show = $(this).text() == text_show;
        rosters.forEach(function(r) { r.show_bench(show); });
        if (show) {
            $(this).text(text_hide);
        } else {
            $(this).text(text_show);
        }
    });
});

});
