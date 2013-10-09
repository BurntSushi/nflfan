$(document).ready(function() {
    $('table.plays').each(function() {
        var $this = $(this);
        var $form = $this.find('thead th form');
        var $link = $this.find('.plays_opts a');
        var $auto = $form.find('input[name="auto-update"]')

        function set_auto() {
            if ($auto.is(':checked')) {
                var id = window.setInterval(function() { $form.submit() }, 10000);
                $form.data('auto-update', id);
            } else {
                var id = $form.data('auto-update');
                if (id) {
                    window.clearInterval(id);
                }
            }
        }

        $link.click(function(ev) {
            ev.preventDefault();
            if ($form.is(':visible')) {
                viewable_hide($form, ev);
            } else {
                viewable_show($form, ev);
            }
        });
        $form.find('input[value="Close"]').click(function(ev) {
            viewable_hide($form, ev);
        });

        $auto.change(function() { set_auto(); });
        $form.find('input').change(function() { $form.submit(); });
        $form.find('select').change(function() { $form.submit(); });
        $form.ajaxForm({
            success: function(r, status, xhr, $f) {
                $tbody = $('tbody', r);
                $this.find('tbody').html($tbody.html());
            }
        });

        set_auto();
    });
});
