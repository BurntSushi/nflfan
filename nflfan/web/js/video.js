function hide_player() {
    $('#vid video').get(0).pause();
    $('#vid').slideUp();
}

function watch_play(gsis_id, play_id) {
    /* $.get('/watch/{0}/{1}'.format(gsis_id, play_id)) */
    var url = '/vid/{0}/{1}'.format(gsis_id, play_id);
    var $vid = $('#vid video');
    var vid = $vid.get(0);

    $vid.attr('src', url);
    vid.load();
    $('#vid').slideDown('fast', function() {
        window.setTimeout(function() { vid.play(); }, 1000);
    });
}

$(document).ready(function() {
    $('#vid button').click(hide_player);
});
