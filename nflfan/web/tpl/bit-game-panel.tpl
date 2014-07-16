<div class="nflfan-panel-game" data-gsis-id="{{ g.gsis_id }}">
  <table class="hidden table table-bordered"
         data-bind="if: game, css: { hidden: !game }">
    <thead>
      <tr class="bg-info">
        <th>
          <span data-bind="css: {
              'text-success': game().home_score > game().away_score,
              'text-danger': game().home_score < game().away_score
            }">
            <span data-bind="text: game().home_team"></span>
            (<span data-bind="text: game().home_score"></span>)
          </span>
          @
          <span data-bind="css: {
              'text-success': game().home_score < game().away_score,
              'text-danger': game().home_score > game().away_score
            }">
            <span data-bind="text: game().away_team"></span>
            (<span data-bind="text: game().away_score"></span>)
          </span>
          <p class="nomarbot">
            <small data-bind="text: nice_start_time()"></small>
          </p>
        </tr>
      </tr>
    </thead>
    <tbody>
      <!-- ko foreach: plays -->
      <tr>
        <td data-bind="text: description"></td>
      </tr>
      <!-- /ko -->
    </tbody>
  </table>
</div>
