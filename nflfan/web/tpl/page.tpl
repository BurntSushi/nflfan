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
          bootstrap: 'ext/bootstrap',
          knockout: 'ext/knockout-3.1.0',
          sprintf: 'ext/sprintf'
        },
        shim: {
          bootstrap: {
            deps: ['jquery']
          }
        }
      };
    </script>
    <script data-main="{{ pagejs }}" src="/js/ext/require.js"></script>

    <link href="/css/bootstrap.min.css" rel="stylesheet">
    <link href="/css/nflfan.css" rel="stylesheet">
  </head>
  <body>
    {{! base }}
  </body>
</html>
