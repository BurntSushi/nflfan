<form role="form" class="form-inline" id="nflfan-panel-game-controls">
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
          <!-- ko foreach: filters.sorts -->
          <div class="row bot15"><div class="col-xs-12">
            <div class="form-group right10">
              <select class="form-control"
                      data-bind="value: field, valueAllowUnset: true,
                                 foreach: $root.sort_fields">
                <option>Field</option>
                <optgroup data-bind="attr: { label: entity }, foreach: fields">
                  <option data-bind="text: $data, value: $data"></option>
                </optgroup>
              </select>
            </div>
            <div class="form-group">
              <label class="radio-inline">
                <input type="radio" value="+"
                       data-bind="attr: { name: $index }, checked: order">
                Ascending
              </label>
              <label class="radio-inline">
                <input type="radio" value="-"
                       data-bind="attr: { name: $index }, checked: order">
                Descending
              </label>
            </div>
            <div class="form-group"
                 data-bind="if: $parent.filters.sorts().length >= 2">
              <button type="button" class="btn btn-default"
                      data-bind="click: function() { $root.remove_sort($data); }">
                Remove
              </button>
            </div>
          </div></div>
          <!-- /ko -->
          <div class="row"><div class="col-xs-12">
            <button type="button" class="btn btn-primary"
                    data-bind="click: add_sort">
              Add another field
            </button>
          </div></div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-primary"
                  data-dismiss="modal">Close</button>
        </div>
      </div>
    </div>
  </div>
</form>
