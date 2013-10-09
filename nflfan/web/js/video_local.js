function watch_play(gsis_id, play_id) {
    $.get('/watch/{0}/{1}'.format(gsis_id, play_id))
}
