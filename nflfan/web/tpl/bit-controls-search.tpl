<!-- ko foreach: filters.search -->
<div class="row bot15">
  <div class="col-xs-6">
    <div class="btn-group">
      <button class="btn btn-default dropdown-toggle"
              type="button" data-toggle="dropdown">
        <!-- ko if: field() -->
          <span data-bind="text: entity() + ' (' + field() + ')'"></span>
        <!-- /ko -->
        <!-- ko if: !field() -->
          <span data-bind="text: entity() + ' (N/A)'"></span>
        <!-- /ko -->
        <span class="caret"></span>
      </button>
      <ul class="dropdown-menu short-dropdown" role="menu">
        <!-- ko foreach: $root.entity_fields[entity()] -->
          <li data-bind="css: { active: $parent.field() == $data }">
            <a href="javascript:void(0)"
               data-bind="text: $data,
                          click: function() { $parent.field($data) }"></a>
          </li>
        <!-- /ko -->
      </ul>
    </div>
  </div>
  <div class="col-xs-6 text-right">
    <div class="btn-group">
      <button class="btn btn-default dropdown-toggle"
              type="button" data-toggle="dropdown">
        <span data-bind="text: op"></span>
        <span class="caret"></span>
      </button>
      <ul class="dropdown-menu short-dropdown" role="menu">
        <!-- ko foreach: ['=', '!=', '<', '<=', '>', '>='] -->
          <li data-bind="css: { active: $parent.op() == $data }">
            <a href="javascript:void(0)"
               data-bind="text: $data,
                          click: function() { $parent.op($data) }"></a>
          </li>
        <!-- /ko -->
      </ul>
    </div>
    <div class="btn-group">
      <input type="text" class="form-control" size="4"
             data-bind="value: value">
    </div>
    <div class="btn-group">
      <button type="button" class="btn btn-default"
              data-bind="click: function() { $root.remove_search($data); }">
        Remove
      </button>
    </div>
  </div>
</div>
<!-- /ko -->

<div class="row"><div class="col-xs-12">
  <h3>Add search field for:</h3>
</div></div>

<div class="row"><div class="col-xs-12">
<!-- ko foreach: available.search_entities -->
  <div class="btn-group">
    <button type="button" class="btn btn-primary"
            data-bind="text: $data,
                       click: function() { $root.add_search($data) }">
    </button>
  </div>
<!-- /ko -->
</div></div>
