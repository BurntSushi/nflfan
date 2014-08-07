% rebase('page.tpl', pagejs='games')

% title = 'NFL games for {season} {phase}, week {week}'.format(**globals())
% include('bit-page-header', page='games', **globals())

% include('bit-controls', **globals())

<div class="bot20"></div>

<%
if len(games) == 0:
  msg = "Could not find any games for {season} {phase}, week {week}."
  msg = msg.format(season=season, phase=phase, week=week)
  include('bit-error', msg=msg)
else:
%>
  <div class="container-fluid"><div class="row">
    % for gs in grouped(3, games):
      % for g in gs:
        <div class="bot30 col-xs-12 col-sm-6 col-md-4 col-lg-3">
          % include('bit-game-panel', g=g)
        </div>
      % end
    % end
  </div></div>
% end
