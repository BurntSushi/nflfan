function hide_player() {
    var $vid = $('#vid video');
    $vid.get(0).pause();
    $vid.removeAttr('src');
    $('#vid').slideUp();
}

function watch_play(gsis_id, play_id) {
    var url = make_vid_url(gsis_id, play_id);
    var $vid = $('#vid video');
    var vid = $vid.get(0);
    
    $vid.css({'width': 'auto', 'height': 'auto'});
    $('#vid').css({'width': 'auto', 'height': 'auto'});

    $vid.attr('src', url);
    vid.load();
    $('#vid').slideDown('fast', function() {
        window.setTimeout(function() { vid.play(); }, 1000);
    });
}

$(document).ready(function() {
    var $div = $('#vid');
    var $vid = $('#vid video');
    var spacing = 100;
    var $win = $(window);
    $('#vid button').click(hide_player);

    window.setInterval(function() {
        if ($div.width() >= ($win.innerWidth() - spacing)) {
            $div.width($win.innerWidth() - spacing);
            $vid.width($div.width());
        }
        if ($div.height() >= ($win.innerHeight() - spacing)) {
            $div.height($win.innerHeight() - spacing);
            $vid.height($div.height() - 50);
        }
    }, 500);
});
