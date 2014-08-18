<div class="nflfan-panel-game hidden"
     data-gsis-id="{{ g.gsis_id }}"
     data-bind="if: game, css: { hidden: !game }">
  <div class="play-header"
       data-bind="attr: { title: game().gsis_id },
                  css: { 'bg-success': game().finished,
                         'bg-danger': game().is_playing,
                         'bg-info': !game().finished && !game().is_playing }">
    <span data-bind="css: {
        'text-success': game().home_score < game().away_score,
        'text-danger': game().home_score > game().away_score
      }">
      <span data-bind="text: game().away_team"></span>
      (<span data-bind="text: game().away_score"></span>)
    </span>
    @
    <span data-bind="css: {
        'text-success': game().home_score > game().away_score,
        'text-danger': game().home_score < game().away_score
      }">
      <span data-bind="text: game().home_team"></span>
      (<span data-bind="text: game().home_score"></span>)
    </span>
    <p class="nomarbot">
      <small data-bind="text: nice_start_time()"></small>
    </p>
  </div>
  <div class="play-table hidden"
       data-bind="css: { hidden: !plays() || plays().length == 0 }">
    <table class="table table-bordered">
      <tbody>
        <!-- ko foreach: plays -->
        <tr>
        % include('bit-play-description', **globals())
        </tr>
        <!-- /ko -->
      </tbody>
    </table>
  </div>
  <div class="play-header text-right hidden"
       data-bind="attr: { title: game().gsis_id },
                  css: { hidden: !plays() || plays().length == 0,
                         'bg-success': game().finished,
                         'bg-danger': game().is_playing,
                         'bg-info': !game().finished && !game().is_playing }">
    <small>
      <a href="/query?entity=play&game_gsis_id={{g.gsis_id}}&sort=-play_id">
        Search plays
      </a>
    </small>
  </div>
</div>
