% auto = 'yes' if defined('auto_update') and auto_update else 'no'
% update = url.fresh('roster', prov=league.prov_name, league=league.name, qstr=url.qstr())
<div class="roster" data-auto-update="{{ auto }}" data-update-url="{{ update }}">
 <table cellspacing="0" cellpadding="0">
  <tr>
    <th colspan="4">
      <p>{{ roster.owner.name }}</p>
      <p class="small">{{ league.full_name }} :: week {{ roster.week }}</p>
    </th>
  </tr>
  % for player in sorted(roster.players, key=lambda rp: rp.bench):
    % classes = []
    % if player.game is not None:
      % if player.game.is_playing:
      %   classes.append('playing')
      % elif player.game.finished:
      %   classes.append('finished')
      % end
    % else:
    %   classes.append('bye')
    % end
    % if player.bench:
    %   classes.append('bench')
    % else:
    %   classes.append('starter')
    % end

    <tr class="{{ ' '.join(classes) }}">
      <td class="position">
        {{ player.position }}
        % if player.bench:
          ({{ player.player.position if player.player else 'DEF' }})
        % end
      </td>
      <td class="team">{{ player.team }}</td>
      <td class="player_name">{{ player.name }}</td>
      <td class="points">
      % if player.game is None:
        BYE
      % else:
        <a href="#"
           data-details-url="{{ url.fresh('details', prov=league.prov_name, league=league.name, player_id=player.player_id, qstr=url.qstr()) }}"
         >{{ player.points }}</a>
      % end
      </td>
    </tr>
  % end
  <tr class="total">
    <td colspan="3">
      <a href="#" data-show="Show bench" data-hide="Hide bench">Show bench</a>
      <p>Total:</p>
    </td>
    <td>{{ roster.points }}</td>
  </tr>
 </table>
</div>

