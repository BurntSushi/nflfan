<!-- ko foreach: filters.sorts -->
<div class="row bot15">
  <div class="col-xs-5">
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
  <div class="col-xs-7 text-right">
    <div class="btn-group">
      <button class="btn btn-default dropdown-toggle"
              type="button" data-toggle="dropdown">
        <!-- ko if: order() == '+' -->
          Ascending
        <!-- /ko -->
        <!-- ko if: order() == '-' -->
          Descending
        <!-- /ko -->
        <span class="caret"></span>
      </button>
      <ul class="dropdown-menu short-dropdown" role="menu">
        <li data-bind="css: { active: order() == '+' }">
          <a href="javascript:void(0)"
             data-bind="click: function() { order('+') }">
            Ascending
          </a>
        </li>
        <li data-bind="css: { active: order() == '-' }">
          <a href="javascript:void(0)"
             data-bind="click: function() { order('-') }">
            Descending
          </a>
        </li>
      </ul>
    </div>
    <div class="btn-group">
      <button type="button" class="btn btn-default"
              data-bind="click: function() { $root.remove_sort($data); }">
        &times;
      </button>
    </div>
  </div>
</div>
<!-- /ko -->

<div class="row"><div class="col-xs-12">
  <h3>Add sort field for:</h3>
</div></div>

<div class="row"><div class="col-xs-12">
<!-- ko foreach: available.sort_entities -->
  <div class="btn-group">
    <button type="button" class="btn btn-primary"
            data-bind="text: $data,
                       click: function() { $root.add_sort($data) }">
    </button>
  </div>
<!-- /ko -->
</div></div>
