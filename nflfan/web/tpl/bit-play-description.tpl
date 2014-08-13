<!-- This assumes that a KO play object is the current context -->
<!-- ko with: drive -->
  <!-- ko with: game -->
  % include('bit-game-cell', **globals())
  <!-- /ko -->
<!-- /ko -->

% include('bit-play-info', **globals())

<td data-bind="
  html: (function() {
    var d = description;
    d = d.replace(/([a-zA-Z]+\.[a-zA-Z]+)/g, '<strong>$1</strong>')
         .replace(/^\([0-9:]+\) */, '');
    return d;
  })()
  "
  ></td>
