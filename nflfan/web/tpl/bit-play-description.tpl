<!-- This assumes that a KO play object is the current context -->
<td data-bind="
  html: (function() {
    var d = description;
    d = d.replace(/([a-zA-Z]+\.[a-zA-Z]+)/g, '<strong>$1</strong>')
         .replace(/^\([0-9:]+\) */, '');
    if (down !== null) {
      d = down + ' and ' + yards_to_go + ', ' + d;
    }
    if (yardline !== null && yardline != 'N/A') {
      d = yardline + ', ' + d;
    }
    d = time + ', ' + d;
    return d;
  })()
  "
  ></td>
