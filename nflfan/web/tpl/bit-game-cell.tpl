<!-- Assumes that a `game` object is the current context. -->
<td style="white-space: nowrap;">
  <span data-bind="css: { 'text-success': home_score < away_score,
                          'text-danger': home_score > away_score }">
    <span data-bind="text: away_team"></span>
    (<span data-bind="text: away_score"></span>)
  </span>
  @
  <span data-bind="css: { 'text-success': home_score > away_score,
                          'text-danger': home_score < away_score }">
    <span data-bind="text: home_team"></span>
    (<span data-bind="text: home_score"></span>)
  </span>

  <br>

  <small>
    <span data-bind="text: season"></span>
    <span data-bind="text: phase"></span>
    , Week <span data-bind="text: week"></span>
  </small>

  <br>

  <small data-bind="text: nice_datetime(new Date(start_time))"></small>
</td>
