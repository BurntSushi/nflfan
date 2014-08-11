% rebase('page.tpl', pagejs='plays')

% title = 'NFL play filter'.format(**globals())
% include('bit-page-header', page='games', **globals())

<div class="bot20"></div>

<div class="container-fluid"><div class="row">
  <div class="col-xs-4">
    <form role="form" class="form" id="nflfan-panel-controls">
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
    </form>
  </div>
  <div class="col-xs-8">
    <div class="nflfan-play-table">
      <div class="play-table hidden"
           data-bind="css: { hidden: !rows() || rows().length == 0 }">
        <table class="table table-bordered">
          <tbody>
            <!-- ko foreach: rows -->
            <tr>
              % include('bit-play-description', **globals())
            </tr>
            <!-- /ko -->
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div></div>
