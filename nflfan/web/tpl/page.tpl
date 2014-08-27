<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Fantasy Football</title>

    <script type="text/javascript">
      var require = {
        baseUrl: '/js',
        paths: {
          jquery: 'ext/jquery-2.1.1',
          jq: 'lib/jquery',
          bootstrap: 'ext/bootstrap',
          knockout: 'ext/knockout-3.1.0',
          sprintf: 'ext/sprintf',
        },
        shim: {
          bootstrap: {
            deps: ['jquery']
          }
        }
      };

      function nice_datetime(t) {
        var options = {
            hour12: true,
            weekday: 'short',
            month: 'short',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        };
        return t.toLocaleDateString(undefined, options);
      }
    </script>
    <script data-main="{{ pagejs }}" src="/js/ext/require.js"></script>

    <link href="/css/bootstrap.min.css" rel="stylesheet">
    <link href="/css/nflfan.css" rel="stylesheet">
  </head>
  <body>
    <div id="loading">Loading...</div>
    <div class="modal fade" id="video" taxindex="-1" role="dialog">
      <div class="modal-dialog modal-lg"><div class="modal-content">
        <div class="modal-header">
          <button type="button" class="close" data-dismiss="modal">
            <span aria-hidden="true">&times;</span>
            <span class="sr-only">Close</span>
          </button>
          <h4 class="modal-title" id="video-title">
            Watch play
          </h4>
        </div>
        <div class="modal-body">
          <video controls="controls" muted="muted" type="video/mp4" style="width: 100%;">
            Your browser does not support the video tag.
          </video>
          <br>
          <small id="video-not-working"><p>Not working? Access the raw video here: <a href="#"></a>.</p></small>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-default" data-dismiss="modal">
            Close
          </button>
        </div>
      </div></div>
    </div>

    {{! base }}
  </body>
</html>
