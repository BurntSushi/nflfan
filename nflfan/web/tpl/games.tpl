% rebase('page.tpl', **globals())

<div class="page-header">
  <div class="row">
    <div class="col-lg-4">
      <h1>{{ season }} {{ phase }}, week {{ week }}</h1>
    </div>
    <div class="col-lg-8 text-right">
      % include('bit-nav', season=season, phase=phase, week=week)
    </div>
  </div>
</div>

<div class="row"><div class="col-xs-12">
  % include('bit-controls')
</div></div>

<div class="row">
% for gs in grouped(3, games):
  % for g in gs:
    <div class="bot30 col-xs-12 col-sm-6 col-md-4 col-lg-3">
      % include('bit-game-panel', g=g)
    </div>
  % end
% end
</div>

