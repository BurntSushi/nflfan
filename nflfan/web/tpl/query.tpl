% rebase('page.tpl', pagejs='query')

% title = 'NFL query'.format(**globals())
% include('bit-page-header', page='query', **globals())

<div class="bot20"></div>

<div class="container-fluid"><div class="row">
  <div class="col-xs-12 col-sm-12 col-md-5 col-lg-4">
    <form role="form" class="form" id="nflfan-panel-controls">
      <div class="panel panel-default hidden"
           data-bind="css: { hidden: false }">
        <div class="panel-heading"><h3 class="panel-title">Search</h3></div>
        <div class="panel-body">
          % include('bit-controls-search')
        </div>
      </div>

      <div class="panel panel-default hidden"
           data-bind="css: { hidden: false }">
        <div class="panel-heading"><h3 class="panel-title">Sort</h3></div>
        <div class="panel-body">
          % include('bit-controls-sort')
        </div>
      </div>

      <div class="panel panel-default hidden"
           data-bind="css: { hidden: false }">
        <div class="panel-heading"><h3 class="panel-title">Limits</h3></div>
        <div class="panel-body">
          <div class="row bot10">
            <div class="col-xs-6">
              <button type="button"
                      class="btn btn-default"
                      data-bind="css: { 'btn-default': !my_players(),
                                        'btn-success': my_players() },
                                 click: function() { my_players(!my_players()); }">
                Limit to my fantasy players
              </button>
            </div>
          </div>
          <div class="row">
            <div class="col-xs-6">
              <select class="form-control" id="limit"
                      data-bind="optionsCaption: 'Limit',
                                 options: available.limits,
                                 value: filters.limit">
              </select>
            </div>
          </div>
        </div>
      </div>
    </form>
  </div>
  <div class="col-xs-12 col-sm-12 col-md-7 col-lg-8">
    <div class="nflfan-query-table hidden"
         data-bind="css: { hidden: !rows() || rows().length == 0 }">
      <div class="row bot15">
        <div class="col-xs-12">
          <span class="lead">Show as:</span>
          &nbsp;&nbsp;&nbsp;
          <!-- ko foreach: show_entities -->
<div class="btn-group">
  <button type="button" class="btn"
          data-bind="text: $data,
                     css: { 'btn-primary': $root.showing() == $data,
                            'btn-default': $root.showing() != $data },
                     click: function() { $root.show_as($data); }">
  </button>
</div>
          <!-- /ko -->
        </div>
      </div>
      <div class="row"><div class="col-xs-12">

<!-- ko if: showing() == 'game' -->
<table class="table table-bordered">
  <tbody>

  <!-- ko foreach: rows -->
  <tr>
    % include('bit-game-cell', **globals())
  </tr>
  <!-- /ko -->

  </tbody>
</table>
<!-- /ko -->

<!-- ko if: showing() == 'drive' -->
<table class="table table-bordered">
  <tbody>

  <!-- ko foreach: rows -->
  <tr>
    <!-- ko with: game -->
    % include('bit-game-cell', **globals())
    <!-- /ko -->
    <td data-bind="text: pos_team"></td>
    <td data-bind="text: result"></td>
    <td>
      From
      <span data-bind="text: start_field"></span>
      (<span data-bind="text: start_time"></span>)
      to
      <span data-bind="text: end_field"></span>
      (<span data-bind="text: end_time"></span>)
    </td>
  </tr>
  <!-- /ko -->

  </tbody>
</table>
<!-- /ko -->

<!-- ko if: showing() == 'play' -->
<table class="table table-bordered">
  <tbody>

  <!-- ko foreach: rows -->
  <tr>
    % include('bit-play-description', **globals())
  </tr>
  <!-- /ko -->

  </tbody>
</table>
<!-- /ko -->

<!-- ko if: showing() == 'play_player' -->
<table class="table table-bordered">
  <tbody>

  <!-- ko foreach: rows -->
  <tr>
    <!-- ko with: play.drive.game -->
    % include('bit-game-cell', **globals())
    <!-- /ko -->
    <!-- ko with: play -->
    % include('bit-play-info', **globals())
    <!-- /ko -->
    % include('bit-play-player', **globals())
  </tr>
  <!-- /ko -->

  </tbody>
</table>
<!-- /ko -->

<!-- ko if: showing() == 'aggregate' -->
<table class="table table-bordered">
  <tbody>

  <!-- ko foreach: rows -->
  <tr>
    <td data-bind="text: player.full_name"></td>
    <td style="white-space: nowrap;" data-bind="foreach: fields">
      <span data-bind="text: $data"></span>:
      <span data-bind="text: $parent[$data]"></span>
      <br>
    </td>
  </tr>
  <!-- /ko -->

  </tbody>
</table>
<!-- /ko -->

<!-- ko if: showing() == 'player' -->
<table class="table table-bordered">
  <thead><tr>
    <th>#</th>
    <th>Player</th>
    <th>Status</th>
    <th>Team</th>
    <th>Position</th>
    <th>Years Pro</th>
    <th>Weight (lbs)</th>
    <th>Height (in)</th>
    <th>College</th>
    <th>Birthdate</th>
  </tr></thead>
  <tbody>

  <!-- ko foreach: rows -->
  <tr>
    <td data-bind="text: uniform_number"></td>
    <td data-bind="text: full_name || gsis_name"></td>
    <td data-bind="text: status"></td>
    <td data-bind="text: team"></td>
    <td data-bind="text: position"></td>
    <td data-bind="text: years_pro"></td>
    <td data-bind="text: weight"></td>
    <td data-bind="text: height"></td>
    <td data-bind="text: college"></td>
    <td data-bind="text: birthdate"></td>
  </tr>
  <!-- /ko -->

  </tbody>
</table>
<!-- /ko -->

      </div></div>

      <div class="row"><div class="col-xs-12">
        <form class="form-inline" role="form">
          <div class="form-group">
            <label class="lead" for="permalink">Permalink:</label>
            <input type="text" class="form-control" size="100"
                   data-bind="value: window.location.origin + permalink()">
          </div>
        </form>
      </div></div>
    </div>
  </div>
</div></div>
