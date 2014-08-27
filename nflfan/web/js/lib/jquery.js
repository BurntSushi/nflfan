define(['jquery'], function($) {
    $(document).ajaxStart(function () {
        $('#loading').fadeIn();
    });
    $(document).ajaxStop(function () {
        $('#loading').fadeOut();
    });
    return $;
});
