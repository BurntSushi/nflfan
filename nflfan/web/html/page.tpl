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

  <script src="http://code.jquery.com/jquery-1.9.1.min.js"></script>
  <!-- <script src="/js/results.js"></script> -->
</head>
<body>
  <div id="content">
    <div class="clearfix">
      % include
    </div>

    <div id="leagues">
      <h2>Your leagues</h2>
      <ul>
      % for prov, leagues in conf.items():
      %   for lg_name, lg in leagues.items():
      %     u = url.fresh('league', prov=prov, league=lg_name)
            <li><a href="{{ u }}">{{ lg.full_name }}</a></li>
      %   end
      % end
      </ul>
    </div>
    % if not defined('notime'):
      <p style="margin-top: 30px;">Execution time: $exec_time$</p>
    % end
  </div>
</body>
</html>
