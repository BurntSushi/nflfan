% rebase page **globals()

<h1>Plays for week {{ week }}</h1>

% for gid in game_order:
  <div class="game_plays">
{{! incl('play_table', week=week, games=games, plays=game_plays[gid], rosters=rosters, auto_update=games[gid].is_playing, title=game_str(games, gid), game_tags=set([gid])) }}
  </div>
% end

