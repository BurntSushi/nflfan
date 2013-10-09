// Simple sprintf taken from: http://goo.gl/iLCwd
// If we need to get fancy, then:
// http://www.diveintojavascript.com/projects/javascript-sprintf
if (!String.prototype.format) {
    String.prototype.format = function() {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) { 
            if (typeof args[number] != 'undefined') {
                return args[number];
            }
            return match;
        });
    };
}

// set_viewable_offset takes a DOM element and an event with mouse information,
// and sets the offset (using jQuery) so that the element is viewable within 
// the window.
// The given mouse coordinates are used as the base of where the element should
// be positioned.
function viewable_show($obj, ev, complete) {
    // Give the box some room.
    var spacing = 10;

    var wtop = $(window).scrollTop();
    var wbot = wtop + $(window).height();
    var wrht = $(window).scrollLeft() + $(window).width();

    $obj.show();
    var height = $obj.outerHeight();
    var width = $obj.outerWidth();
    $obj.hide();

    var otop = ev.pageY;
    var olft = ev.pageX;
    var obot = otop + height;
    var orht = olft + width;
    $obj.data('origin', 'top');

    if (obot + spacing > wbot && otop - height >= wtop) {
        $obj.data('origin', 'bottom');
        otop -= height;
    }
    if (orht + spacing > wrht) {
        olft -= width;
    }

    $obj.show();
    $obj.offset({top: otop + 3, left: olft});
    $obj.hide();

    if ($obj.data('origin') == 'top') {
        $obj.show('slide', {
            complete: complete,
            duration: 200,
            direction: 'up'
        });
    } else {
        $obj.show('slide', {
            complete: complete,
            duration: 200,
            direction: 'down'
        });
    }
}

function viewable_hide($obj, complete) {
    if ($obj.data('origin') == 'top') {
        $obj.hide('slide', {
            complete: complete,
            duration: 200,
            direction: 'up'
        });
    } else {
        $obj.hide('slide', {
            complete: complete,
            duration: 200,
            direction: 'down'
        });
    }
}
