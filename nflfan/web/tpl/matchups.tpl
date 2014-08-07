% rebase('page.tpl', pagejs='leagues')

% title = 'Your fantasy matchups for {season} {phase}, week {week}'.format(**globals())
% include('bit-page-header', page='matchups', **globals())

<div class="bot20"></div>

<%
if len(leagues) == 0:
  msg = "Could not find any matchups for {season} {phase}, week {week}."
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
    % for lg in leagues:
      <div class="row"><div class="col-xs-12">
        <h2 class="text-center">{{ lg.name }}</h4>
      </div></div>
      <div class="row">
        % owner = lg.me(lg.owners(week))
        % matchup = lg.matchup(week, owner.ident)
        % opponent = matchup.other(owner.ident)

        <div class="bot30 col-xs-6">
          <div style="max-width: 400px; margin-left: auto;">
            % include('bit-fan-roster', league=lg, week=week, owner=owner,
            %                           is_matchup=True)
          </div>
        </div>
        <div class="bot30 col-xs-6">
          <div style="max-width: 400px; margin-right: auto;">
            % include('bit-fan-roster', league=lg, week=week, owner=opponent,
            %                           is_matchup=True)
          </div>
        </div>
      </div>
    % end
  </div>
% end
