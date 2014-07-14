<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Bootstrap 101 Template</title>

    <script type="text/javascript">
      var require = {
        baseUrl: '/js',
        paths: {
          jquery: 'lib/jquery-2.1.1',
          bootstrap: 'lib/bootstrap',
          knockout: 'lib/knockout-3.1.0',
          underscore: 'lib/underscore',
          'underscore.string': 'lib/underscore.string',
          text: 'lib/text'
        },
        shim: {
          bootstrap: {
            deps: ['jquery']
          }
        }
      };
    </script>
    <script data-main="index" src="/js/lib/require.js"></script>

    <!-- Bootstrap -->
    <link href="/css/bootstrap.min.css" rel="stylesheet">
    <link href="/css/bootstrap-theme.min.css" rel="stylesheet">
    <link href="/css/nflfan.css" rel="stylesheet">

  </head>
  <body>
    <div class="container-fluid">
      {{! base }}
    </div>
  </body>
</html>
