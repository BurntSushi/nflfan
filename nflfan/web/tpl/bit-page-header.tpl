<div class="container-fluid"><div class="page-header nomarbot">
  <div class="row"><div class="col-xs-12">
    <h1 class="nomartop">{{ title }}</h1>
  </div></div>
  <div class="row">
    <div class="col-xs-12 col-sm-7 col-md-8 col-lg-9">
      % include('bit-views', **globals())
    </div>
    <div class="col-xs-12 col-sm-5 col-md-4 col-lg-3 text-right">
      % include('bit-nav', **globals())
    </div>
  </div>

</div></div>


<div id="nflfan-error" class="container hidden nomarbot"
     style="margin-top: 15px;">
  <div class="row nomarbot"><div class="col-xs-12 nomarbot">
    <div class="alert alert-danger alert-dismissible nomarbot" role="alert">
      <button type="button" class="close">
        <span aria-hidden="true">&times;</span>
        <span class="sr-only">Close</span>
      </button>
      <p></p>
    </div>
  </div></div>
</div>

