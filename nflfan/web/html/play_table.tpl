<table class="plays" cellspacing="0" cellpadding="0">
  % for p in plays:
  <tr>
    <td class="nowrap">{{ game_str(games, p.gsis_id) }}</td>
    <td class="nowrap">{{ p.time }}</td>
    <td>{{ clean_play_desc(p.description) }}</td>
  </tr>
  % end
</table>

