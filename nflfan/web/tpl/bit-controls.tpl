<div class="container-fluid"
     style="padding-top: 10px; padding-bottom: 10px; background: #f5f5f5;">
  <form role="form" class="form-inline" id="nflfan-panel-controls">
    <div class="form-group">
      <div class="form-control-static">
        <p style="font-weight: semibold;
                  font-size: 22px;
                  margin: 0 10px 0 0;">Play filtering</p>
      </div>
    </div>
    <div class="form-group">
      <label for="limit" class="control-label sr-only">Limit</label>
      <select class="form-control" id="limit"
              data-bind="optionsCaption: 'Limit',
                         options: available.limits,
                         value: filters.limit">
      </select>
    </div>
    <button type="button" class="btn btn-primary"
            data-toggle="modal"
            data-target="#controls-sort-fields">Sort by</button>

    <div class="modal fade" id="controls-sort-fields" tabindex="-1"
         role="dialog" aria-labeledby="controls-sort-fields-label"
         aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal">
              <span aria-hidden="true">&times;</span>
              <span class="sr-only">Close</span>
            </button>
            <h4 class="modal-title" id="controls-sort-fields-label">
              Sort fields
            </h4>
          </div>
          <div class="modal-body">
            % include('bit-controls-sort')
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary"
                    data-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <button type="button" class="btn btn-primary"
            data-toggle="modal"
            data-target="#controls-search-fields">Filter by</button>

    <div class="modal fade" id="controls-search-fields" tabindex="-1"
         role="dialog" aria-labeledby="controls-search-fields-label"
         aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal">
              <span aria-hidden="true">&times;</span>
              <span class="sr-only">Close</span>
            </button>
            <h4 class="modal-title" id="controls-sort-fields-label">
              Search fields
            </h4>
          </div>
          <div class="modal-body">
            % include('bit-controls-search')
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary"
                    data-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
    <div class="form-group">
      <button type="button"
              class="btn btn-default"
              data-bind="css: { 'btn-default': !my_players(),
                                'btn-success': my_players() },
                         click: function() { my_players(!my_players()); }">
        Limit to my fantasy players
      </button>
    </div>
  </form>
</div>
