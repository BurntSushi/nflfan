<div class="roster"><table cellspacing="0" cellpadding="0">
  <tr>
    <th colspan="4">
      <p>{{ roster.owner.name }}</p>
      <p class="small">{{ league.full_name }} :: week {{ roster.week }}</p>
    </th>
  </tr>
  % for player in roster.players:
    % if player.game is not None:
      % if player.game.is_playing:
        <tr class="playing">
      % elif player.game.finished:
        <tr class="finished">
      % else:
        <tr>
      % end
    % else:
      <tr class="bye">
    % end

      <td>{{ player.position }}</td>
      <td>{{ player.team }}</td>
      <td>{{ player.name }}</td>
      <td class="points">{{ "BYE" if player.game is None else player.points }}</td>
    </tr>
  % end
  <tr class="total">
    <td colspan="3">Total:</td>
    <td>{{ roster.points }}</td>
  </tr>
</table></div>

