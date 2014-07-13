$(document).ready(function() {
    $('.roster').each(function() {
        var $roster = $(this);
        var $sdeets = $('#score_details');

        function attach() {
            $roster.find('tr.total a').click(function(ev) {
                $a = $(this);
                ev.preventDefault();
                if ($a.text() == $a.data('show')) {
                    $roster.find('tr.bench').show();
                    $a.text($a.data('hide'));
                } else {
                    $roster.find('tr.bench').hide();
                    $a.text($a.data('show'));
                }
            });
            $roster.find('td.points a').click(function(ev) {
                $a = $(this);
                ev.preventDefault();
                $.get($a.data('details-url'), function(data, s, xhr) {
                    $data = $(data);
                    $sdeets.html($data.html());
                    viewable_show($sdeets, ev);

                    $sdeets.find('a').click(function(ev) {
                        ev.preventDefault();
                        viewable_hide($sdeets, ev);
                    });
                });
            });
        }

        function update(data, textStatus, xhr) {
            $nr = $(data);
            $olda = $roster.find('tr.total a');
            if ($olda.text() == $olda.data('show')) {
                $nr.find('tr.bench').hide();
            } else {
                $nr.find('tr.bench').show();
            }
            $nr.find('tr.total a').text($olda.text());
            $roster.html($nr.html());
            attach();
        }

        if ($roster.data('auto-update') == 'yes') {
            window.setInterval(function() {
                $.get($roster.data('update-url'), update);
            }, 10000);
        }

        attach();
    });
});
