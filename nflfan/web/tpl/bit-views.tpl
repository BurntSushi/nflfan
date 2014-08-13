<%
def show_active(which):
  if which == page:
    return ' class="active"'
  else:
    return ''
  end
end
%>
<ul class="pagination pagination nomarbot nomartop">
  <li{{! show_active('leagues') }}>
    <a href="/seasons/{{season}}/phases/{{phase}}/weeks/{{week}}/leagues">
      Fantasy teams
    </a>
  </li>
  <li{{! show_active('matchups') }}>
    <a href="/seasons/{{season}}/phases/{{phase}}/weeks/{{week}}/matchups">
      Fantasy matchups
    </a>
  </li>
  <li{{! show_active('query') }}>
    <a href="/query?game_season_year={{season}}&game_season_type={{phase}}&game_week={{week}}&sort=-play_id">Plays</a>
  </li>
  <li{{! show_active('games') }}>
    <a href="/seasons/{{season}}/phases/{{phase}}/weeks/{{week}}/games">Games</a>
  </li>
</ul>

<ul class="pagination pagination nomarbot nomartop">
  <li><a href="/">Current plays</a></li>
  <li><a href="/">Current games</a></li>
</ul>
