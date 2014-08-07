% matchup = league.matchup(week, owner.ident)
% opponent = matchup.other(owner.ident)
<div class="nflfan-panel-fanroster hidden"
     data-league-name="{{ league.name }}"
     data-week="{{ week }}"
     data-owner-id="{{ owner.ident }}"
     data-owner-name="{{ owner.name }}"
     data-opponent-id="{{ opponent.ident }}"
     data-opponent-name="{{ opponent.name }}"
     data-bind="css: { hidden: !roster }">
  <div class="popover-content hide">
    <table class="table table-bordered table-striped">
      <thead>
        <tr>
          <th>Category</th><th>#</th><th>Points</th>
        </tr>
      </thead>
      <tbody>
      <!-- ko foreach: player_details -->
        <tr>
          <td data-bind="text: name"></td>
          <td class="text-right" data-bind="text: count.toFixed(2)"></td>
          <td class="text-right" data-bind="text: points.toFixed(2)"></td>
        </tr>
      <!-- /ko -->
      </tbody>
    </table>
  </div>
  <table class="table table-bordered table-striped">
    <thead>
      <tr data-bind="css: { success: any_playing }">
        % if get('is_matchup', False):
          <th colspan="3">{{owner.name}}</th>
        % else:
          <th colspan="3">{{ league.name }} (vs. {{ opponent.name }})</th>
        % end
        <th><small>({{ league.prov_name }})</small></th>
      </tr>
    </thead>
    <tbody data-bind="foreach: roster">
      <tr data-bind="if: !bench || $root.show_bench,
                     css: { danger: game && game.is_playing,
                            strong: game && game.is_playing }">
        <td data-bind="text: position"></td>
        <td data-bind="text: team"></td>
        <td data-bind="text: (player && player.full_name) || team"></td>
        <td class="text-right">
          <a href="#" tabindex="0" rel="popover"
             data-bind="text: points.toFixed(2),
                        click: function(rp, ev) {
                                 $root.show_player_details(rp, ev);
                                }"></a>
        </td>
      </tr>
    </tbody>
    <tfoot>
      % textcls = 'text-success' if lg.is_me(owner) else 'text-danger'
      <tr class="strong {{textcls}}">
        <td colspan="3" class="text-right">Total:</td>
        <td data-bind="text: total().toFixed(2)"></td>
      </tr>
      % if not get('is_matchup', False):
        <tr class="strong text-danger">
          <td colspan="3" class="text-right">{{ opponent.name }}</td>
          <td data-bind="text: opponent_points().toFixed(2)"></td>
        </tr>
      % end
    </tfoot>
  </table>
</div>
