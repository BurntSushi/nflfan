<table cellspacing="0" cellpadding="0" border="0">
  <tr>
    <th>Field</th>
    <th>Stat</th>
    <th>Points</th>
  </tr>

  % total = 0.0
  % for cat in sorted(details):
  % stat, pts = details[cat]
  % total += pts
    <tr>
      <td>{{ cat }}</td>
      <td>{{ stat }}</td>
      <td>{{ pts }}</td>
    </tr>
  % end

  <tr class="dtotal"><td colspan="2">Total</td><td>{{ total }}</td></tr>
  <tr class="close"><td colspan="3"><a href="#">Close</a></td></tr>
</table>
