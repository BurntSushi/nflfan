% rebase page **globals()

<h1>Your teams for week {{ week }}</h1>

% if len(rosters) == 0:
  <p class="error">
    nflfan could not find any teams belonging to you in your configuration.
    Please make sure you've set the <code>me</code> option in each of your
    leagues.
  </p>
% else:
  % for lg, roster in zip(leagues, rosters):
  % include roster league=lg, roster=roster
  % end
% end

% if defined('plays'):
{{! incl('play_table', games=games, plays=plays, rosters=rosters) }}
% end

