<!doctype html>
<!--[if lt IE 7]> <html class="no-js lt-ie9 lt-ie8 lt-ie7" lang="en"> <![endif]-->
<!--[if IE 7]>		<html class="no-js lt-ie9 lt-ie8" lang="en"> <![endif]-->
<!--[if IE 8]>		<html class="no-js lt-ie9" lang="en"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js" lang="en"> <!--<![endif]-->
<head>
	<meta charset="utf-8">

  % if defined('title'):
    <title>{{ title }} :: nflfan web interface</title>
  % else:
    <title>nflfan web interface</title>
  % end

	<meta name="description"
        content="A web interface to view your fantasy football leagues.">

	<link rel="stylesheet" href="/css/normalize.css">
	<link rel="stylesheet" href="/css/style.css">
	<link rel="stylesheet" href="/css/print.css">

  <script type="text/javascript">
  % if conf.get('footage_pbp_url', ''):
    footage_pbp_url = "{{ conf['footage_pbp_url'] }}";
    function make_vid_url(gsis_id, play_id) {
      var splay = play_id.toString();
      if (splay.length < 4) {
        splay = Array(1 + (4 - splay.length)).join("0") + splay;
      }
      return '{0}/{1}/{2}.mp4'.format(footage_pbp_url, gsis_id, splay);
    }
  % else:
    footage_pbp_url = "/vid";
    function make_vid_url(gsis_id, play_id) {
      return '{0}/{1}/{2}'.format(footage_pbp_url, gsis_id, play_id);
    }
  % end
  </script>

  <script src="/js/jquery.min.js"></script>
  <script src="/js/jquery-ui.js"></script>
  <script src="/js/jquery.form.js"></script>

  <script src="/js/util.js"></script>
  <script src="/js/play_table.js"></script>
  <script src="/js/roster.js"></script>
  % if conf.get('video_local', False):
    <script src="/js/video_local.js"></script>
  % else:
    <script src="/js/video.js"></script>
  % end
</head>
<body>
  % if conf.get('message', ''):
    <p id="message">{{ conf['message'] }}</p>
  % end

  % if not conf.get('video_local', False):
    <div id="vid">
      <p><button>Close</button></p>
      <video controls="controls" muted="muted" type="video/mp4">
          Your browser does not support the video tag.
      </video>
    </div>
  % end

  <div id="content">
    <div class="clearfix">
      % include
    </div>

    <div id="footer">

      <!--
      <div>
        <h2>Your leagues</h2>
        <ul>
        % for prov, leagues in conf['leagues'].items():
        %   for lg_name, lg in leagues.items():
        %     u = url.fresh('league', prov=prov, league=lg_name)
              <li><a href="{{ u }}">{{ lg.full_name }}</a></li>
        %   end
        % end
        </ul>
      </div>
      -->

      <div>
        <h2>Navigation</h2>
        <ul>
          <li><a href="{{ url.fresh('week') }}">Current week</a></li>
          <li><a href="{{ url.fresh('plays') }}">Plays around the league</a></li>
        </ul>
      </div>

      <div>
        <h2>Week</h2>
        <ul id="weeks">
        % cweek = get_week()
        % for i in xrange(1, 18):
        %   if i == cweek:
              <li class="current_week">{{ i }}</li>
        %   else:
              <li><a href="{{ url.same(week=i) }}">{{ i }}</a></li>
        %   end
        % end
        </ul>
      </div>
    </div>
    % if not defined('notime'):
      <p style="margin-top: 30px;">Execution time: $exec_time$</p>
    % end
  </div>
</body>
</html>
