<!-- This assumes that a KO play object is the current context -->
<!-- ko with: drive -->
  <!-- ko with: game -->
  % include('bit-game-cell', **globals())
  <!-- /ko -->
<!-- /ko -->

% include('bit-play-info', **globals())

<td>
  <!-- ko if: video_url -->
    <a href="javascript:void(0);"
       title="watch play"
       data-bind="click: function() { $root.controls.watch_play($data); }">
       <span class="glyphicon glyphicon-facetime-video"></span></a>
    &nbsp;
  <!-- /ko -->
  <span data-bind="
    html: (function() {
      var d = description;
      d = d.replace(/([a-zA-Z]+\.[a-zA-Z]+)/g, '<strong>$1</strong>')
           .replace(/^\([0-9:]+\) */, '');
      return d;
    })()
    "
    ></span>
</td>
