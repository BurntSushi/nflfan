<div class="container-fluid"><div class="page-header nomarbot">
  <div class="row"><div class="col-xs-12">
    <h1 class="nomartop">{{ title }}</h1>
  </div></div>
  <div class="row">
    <div class="col-xs-6 col-sm-6 col-md-7 col-lg-8">
      % include('bit-views', **globals())
    </div>
    <div class="col-xs-6 col-sm-6 col-md-5 col-lg-4 text-right">
      % include('bit-nav', **globals())
    </div>
  </div>
</div></div>
