<!-- This assumes that a KO play object is the current context -->
<!-- ko with: drive -->
  <!-- ko with: game -->
  <td style="white-space: nowrap;">
    <span data-bind="css: { 'text-success': home_score < away_score,
                            'text-danger': home_score > away_score }">
      <span data-bind="text: away_team"></span>
      (<span data-bind="text: away_score"></span>)
    </span>
    @
    <span data-bind="css: { 'text-success': home_score > away_score,
                            'text-danger': home_score < away_score }">
      <span data-bind="text: home_team"></span>
      (<span data-bind="text: home_score"></span>)
    </span>

    <br>

    <small>
      <span data-bind="text: season"></span>
      <span data-bind="text: phase"></span>
      , Week <span data-bind="text: week"></span>
    </small>
  </td>
  <!-- /ko -->
<!-- /ko -->
<td style="white-space: nowrap;"
    data-bind="
  html: (function() {
    var d = time + ', ' + pos_team;
    var position = '';
    if (down !== null) {
      var down_txt = '1st';
      if (down == 2) {
        down_txt = '2nd';
      } else if (down == 3) {
        down_txt == '3rd';
      } else if (down == 4) {
        down_txt == '4th';
      }
      position += down_txt + ' and ' + yards_to_go;
    }
    if (yardline !== null && yardline != 'N/A') {
      if (position.length > 0) {
        position += ', ';
      }
      position += yardline;
    }
    if (position.length > 0) {
      d += '<br><small>' + position + '</small>';
    }
    return '<small>' + d + '</small>';
  })()
  "></td>
<td data-bind="
  html: (function() {
    var d = description;
    d = d.replace(/([a-zA-Z]+\.[a-zA-Z]+)/g, '<strong>$1</strong>')
         .replace(/^\([0-9:]+\) */, '');
    return d;
  })()
  "
  ></td>
