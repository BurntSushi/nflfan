<table class="roster" cellspacing="0" cellpadding="0">
  <tr>
    <th colspan="4">
      <p>{{ roster.owner.name }}</p>
      <p class="small">Week {{ roster.week }} :: {{ league.full_name }}</p>
    </th>
  </tr>
  % for player in roster.players:
    <tr>
      <td>{{ player.position }}</td>
      <td>{{ player.team }}</td>
      <td>{{ player.name }}</td>
      <td>{{ player.points }}</td>
    </tr>
  % end
  <tr class="total">
    <td colspan="3">Total:</td>
    <td>{{ roster.points }}</td>
  </tr>
</table>

