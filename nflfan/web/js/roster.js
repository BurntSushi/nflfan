$(document).ready(function() {
    $('.roster').each(function() {
        var $roster = $(this);

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

        window.setInterval(function() {
            $.get($roster.data('update-url'), update);
        }, 10000);

        attach();
    });
});
