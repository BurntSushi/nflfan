% _, my_ids = player_ids(rosters)
%
% def ptag_mine(p):
%   for pp in p.play_players:
%     if pp.player_id in my_ids:
%       return 'mine'
%     end
%   end
%   return ''
% end
%
% def ptag_big(p):
%   thresholds = [
%     ('points', 1), ('fumbles_tot', 1), ('defense_sk', 1), ('defense_int', 1),
%     ('defense_xpblk', 1), ('kicking_fgmissed', 1), ('kicking_rec', 1),
%     ('kicking_xpmissed', 1), ('punting_blk', 1), ('fourth_down_att', 1),
%     ('passing_twoptmissed', 1), ('receiving_twoptmissed', 1),
%     ('rushing_twoptmissed', 1),
%
%     ('kickret_yds', 35), ('passing_yds', 20), ('receiving_yds', 20),
%     ('rushing_yds', 10),
%   ]
%   if any(getattr(p, f, 0) >= v for f, v in thresholds):
%     return 'big'
%   end
%   return ''
% end
%
% def ptag_score(p):
%   if p.points > 0:
%     return 'score'
%   end
%   return ''
% end
%
% def ptag_penalty(p):
%   if p.penalty > 0:
%     return 'penalty'
%   end
%   return ''
% end
%
% taggers = [v for k, v in globals().items() if k.startswith('ptag_')]

<table class="plays" cellspacing="0" cellpadding="0">
  <tr>
    <th colspan="3">Plays</th>
  </tr>

  % limit = int(qget('limit', 100))
  % only_show = set(query().getall('tags'))

  % count = 0
  % for p in plays:
  %   tags = filter(lambda x: x, map(lambda f: f(p), taggers))
  %   if only_show and not only_show.intersection(tags):
  %     continue
  %   end
  %
  %   count += 1
  %   if count > limit:
  %     break
  %   end
  %
  %   # If we only want to see one tag, we don't need to call attention to it.
  %   if len(only_show) == 1:
  %     tags = filter(lambda x: x not in only_show, tags)
  %   end

      <tr class="{{ ' '.join(tags) }}">
        <td class="nowrap">{{ game_str(games, p.gsis_id) }}</td>
        <td class="nowrap"><a href="{{ url.play(p) }}">{{ p.time }}</a></td>
        <td>{{ clean_play_desc(p.description) }}</td>
      </tr>
  % end
</table>

