define(['jq'], function($) {

function Video($node) {
    var self = this;

    self.$node = $node;
    self.$title = $node.find('#video-title');
    self.$notworking = $node.find('#video-not-working');
    self.$v = $node.find('video');
    self.v = self.$v[0];

    self.$node.on('shown.bs.modal', function() {
        window.setTimeout(function() { self.v.play(); }, 500);
    });
    self.$node.on('hide.bs.modal', function() {
        self.v.pause();
    });
    self.$node.on('hidden.bs.modal', function() {
        self.$v.removeAttr('src');
    });
}

Video.prototype.watch = function(title, url) {
    var self = this;

    self.$notworking.find('a').attr('href', url);
    self.$notworking.find('a').html(url);

    self.$title.html(title);
    self.$v.attr('src', url);
    self.v.load();
    self.$node.modal('show');
};

return Video;

});
