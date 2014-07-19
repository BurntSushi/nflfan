<div class="nflfan-weeks"
     data-season="{{season}}" data-phase="{{phase}}" data-week="{{week}}">
  <ul class="pagination nomartop nomarbot">
    <!-- ko foreach: seasons -->
      <!-- ko if: $data == $parent.season -->
        <li class="active">
          <span><strong data-bind="text: $data"></strong></span>
        </li>
      <!-- /ko -->
      <!-- ko if: $data != $parent.season -->
        <li><a href="#"
               data-bind="text: $data,
                          attr: { href: $parent.url('seasons', $data) }"
               ></a></li>
      <!-- /ko -->
    <!-- /ko -->
  </ul>
  <ul class="pagination nomartop nomarbot">
    <!-- ko foreach: phases -->
      <!-- ko if: $data == $parent.phase -->
        <li class="active">
          <span><strong data-bind="text: $data"></strong></span>
        </li>
      <!-- /ko -->
      <!-- ko if: $data != $parent.phase -->
        <li><a href="#"
               data-bind="text: $data,
                          attr: { href: $parent.url('phases', $data) }"
               ></a></li>
      <!-- /ko -->
    <!-- /ko -->
  </ul>
  <br>
  <ul class="pagination nomartop">
    <!-- ko foreach: weeks -->
      <!-- ko if: $data == $parent.week -->
        <li class="active">
          <span><strong data-bind="text: $data"></strong></span>
        </li>
      <!-- /ko -->
      <!-- ko if: $data != $parent.week -->
        <li><a href="#"
               data-bind="text: $data,
                          attr: { href: $parent.url('weeks', $data) }"
               ></a></li>
      <!-- /ko -->
    <!-- /ko -->
  </ul>
</div>
