<div class="nflfan-weeks"
     data-season="{{season}}" data-phase="{{phase}}" data-week="{{week}}">

  <div class="btn-group">
    <div class="btn-group btn-group-lg">
      <button class="btn btn-default dropdown-toggle"
              type="button"
              id="nav-week"
              data-toggle="dropdown">
        {{ season }}
        <span class="caret"></span>
      </button>
      <ul class="dropdown-menu dropdown-menu-right short-dropdown"
          role="menu" aria-labelledby="nav-season">
        <!-- ko foreach: seasons -->
          <li data-bind="css: { active: $data == $parent.season }">
            <a href="#"
               data-bind="text: $data,
                          attr: { href: $parent.url('seasons', $data) }"
               ></a>
          </li>
        <!-- /ko -->
      </ul>
    </div>

    <div class="btn-group btn-group-lg">
      <button class="btn btn-default dropdown-toggle"
              type="button"
              id="nav-week"
              data-toggle="dropdown">
        {{ phase }}
        <span class="caret"></span>
      </button>
      <ul class="dropdown-menu dropdown-menu-right short-dropdown"
          role="menu" aria-labelledby="nav-phase">
        <!-- ko foreach: phases -->
          <li role="presentation"
              data-bind="css: { active: $data == $parent.phase }">
            <a href="#"
               role="menuitem" tabindex="-1"
               data-bind="text: $data,
                          attr: { href: $parent.url('phases', $data) }"
               ></a>
          </li>
        <!-- /ko -->
      </ul>
    </div>

    <div class="btn-group btn-group-lg">
      <button class="btn btn-default dropdown-toggle"
              type="button"
              id="nav-week"
              data-toggle="dropdown">
        Week
        {{ week }}
        <span class="caret"></span>
      </button>
      <ul class="dropdown-menu dropdown-menu-right short-dropdown"
          role="menu" aria-labelledby="nav-week">
        <!-- ko foreach: weeks -->
          <li role="presentation"
              data-bind="css: { active: $data == $parent.week }">
            <a href="#"
               role="menuitem" tabindex="-1"
               data-bind="text: $data,
                          attr: { href: $parent.url('weeks', $data) }"
               ></a>
          </li>
        <!-- /ko -->
      </ul>
    </div>
  </div>
</div>
