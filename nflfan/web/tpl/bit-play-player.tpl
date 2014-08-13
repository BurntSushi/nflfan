<!-- This assumes that a play_player object is the current KO context. -->
<!-- This also assumes that `$root` is a `QueryTable`. -->
<td data-bind="text: player.full_name"></td>
<td data-bind="text: team"></td>
<td style="white-space: nowrap;" data-bind="foreach: fields">
  <span data-bind="text: $data"></span>:
  <span data-bind="text: $parent[$data]"></span>
  <br>
</td>
<td data-bind="text: play.description"></td>
