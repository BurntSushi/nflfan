% started, benched = player_ids(rosters)
%
% def ptag_started(p):
%   for pp in p.play_players:
%     if pp.player_id in started:
%       return 'started'
%     end
%   end
%   return ''
% end
%
% def ptag_bench(p):
%   for pp in p.play_players:
%     if pp.player_id in benched:
%       return 'bench'
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
% taggers = sorted((v for k, v in globals().items() if k.startswith('ptag_')),
%                  key=lambda f: f.__name__)
% only_show = set(query().getall('tags'))
% automatic = defined('auto_update') and auto_update
% if not defined('limit'):
%   limit = int(qget('limit', 100))
% end
% if not defined('game_tags'):
%   game_tags = set(query().getall('tag_games'))
% end

<table class="plays" cellspacing="0" cellpadding="0">
  <thead>
    <tr>
      <th colspan="3">
        <p class="plays_title">{{ title if defined('title') else 'Plays' }}</p>
        <p class="plays_opts"><a href="#">Display options</a></p>
        <form method="get" action="{{ url.fresh('play-table') }}">
          <input type="hidden" name="week" value="{{ week }}" />
          <input type="hidden" name="is_game" value="{{ qget('is_game', '') }}" />
          <div>
            % id = genid('auto_update')
            <label for="{{ id }}">
              <input type="checkbox" name="auto-update" id="{{ id }}"
                     {{ 'checked="checked"' if automatic else '' }} />
              Auto-update
            </label>
          </div>

          Limit: <input type="text" name="limit" value="{{ limit }}" />
          <input type="button" value="Close" />
          <div>
          % for t in taggers:
          %   t = t.__name__[5:]
          %   id = genid('tag_%s' % t)
            <label for="{{ id }}">
              <input type="checkbox" name="tags" value="{{ t }}" id="{{ id }}"
                     {{ 'checked="checked"' if t in only_show else '' }} />
              {{ t }}
            </label>
          % end
          </div>

          <hr />

          <select name="tag_players">
            <option value="">- Select Player -</option>
          % if qget('is_game', False):
          %   players = players_in_games(list(game_tags))
          % else:
          %   players = players_from_rosters(rosters)
          % end
          % players = sorted(players, key=lambda p: (p.position, p.full_name))

          % for p in players:
            <option value="{{ p.player_id }}">{{ p.position }} {{ p.full_name }}</option>
          % end
          </select>

          <hr />

          % gids = sorted(set(g.gsis_id for g in games.values()))
          % for gid in gids:
          %   id = genid('tag_games_%s' % gid)
              <div>
                <label for="{{ id }}">
                  <input type="checkbox" name="tag_games"
                         value="{{ gid }}" id="{{ id }}"
                         {{ 'checked="checked"' if gid in game_tags else '' }} />
                  {{ game_str(games, gid) }}
                </label>
              </div>
          % end
        </form>
      </th>
    </tr>
  </thead>

  <tbody>
% count = 0
% for p in plays:
%   tags = set(filter(lambda x: x, map(lambda f: f(p), taggers)))
%   if only_show and not only_show.issubset(tags):
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
        % if not qget('is_game'):
          <td class="nowrap">{{ game_str(games, p.gsis_id) }}</td>
        % end
        <td class="nowrap">{{ play_context(p) }}</td>
        <td>
          <p class="play_desc">{{ clean_play_desc(p.description) }}</p>
          % if play_video_exists(p):
            <div class="video_link">
              <a href="javascript:watch_play('{{ p.gsis_id }}', {{ p.play_id }});">watch</a>
            </div>
          % end
        </td>
      </tr>
% end
  </tbody>
</table>

