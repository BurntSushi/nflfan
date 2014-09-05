<!-- This assumes that a KO play object is the current context -->
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
        down_txt = '3rd';
      } else if (down == 4) {
        down_txt = '4th';
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
