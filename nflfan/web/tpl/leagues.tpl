% rebase('page.tpl', pagejs='leagues')

% title = 'Your fantasy teams for {season} {phase}, week {week}'.format(**globals())
% include('bit-page-header', page='leagues', **globals())

<div class="bot20"></div>

<%
if len(leagues) == 0:
  msg = "Could not find any leagues for {season} {phase}, week {week}."
  msg = msg.format(season=season, phase=phase, week=week)
  include('bit-error', msg=msg)
else:
%>
  <div class="container-fluid">
    <div class="row">
      <div class="col-xs-12">
        <p class="lead"><a href="#" id="bench-toggle"></a></p>
      </div>
    </div>
    <div class="row">
    % for lgs in grouped(3, leagues):
      % for lg in lgs:
        <div class="bot30 col-xs-12 col-sm-6 col-md-4 col-lg-3">
          % owner = lg.me(lg.owners(week))
          % include('bit-fan-roster', league=lg, week=week, owner=owner)
        </div>
      % end
    % end
    </div>
  </div>
% end
