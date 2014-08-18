define(['jquery'], function($) {
return {
    // Creates a URL given an array of path components in `pieces` and an
    // optional `params` object specifying the query string. (`params` is
    // passed directly to `jQuery.param`.)
    make: function(pieces, params) {
        // Use "traditional" serialization, e.g., `a=1&a=2` not `a[]=1&a[]=2`.
        var params = $.param(params || {}, true);
        var path = pieces.join('/');
        if (params.length > 0) {
            path += '?';
        }
        return ('/' + path + params).replace(/\+/g, '%20');
    },
    // Given a properly encoded URL, return its query parameters as an object.
    // Keys correspond to query parameters and values are decoded.
    // Values can be strings or arrays of strings. An array of strings is
    // only created when a parameter appears more than once.
    // e.g., `a=1&a=2` would result in `a: [1, 2]`.
    // Note that `a[]=1&a[]=2` is not recognized.
    params: function(url) {
        url = url || '';
        var params = {};
        var start = url.indexOf('?');
        if (start == -1) {
            return params;
        }
        url.substring(start+1).split('&').map(function(keyval) {
            keyval = keyval.split('=');
            if (keyval.length <= 1) { return; }

            var param = decodeURIComponent(keyval[0]),
                value = decodeURIComponent(keyval[1]);
            if (typeof params[param] == "string") {
                params[param] = [params[param], value];
            } else if (typeof params[param] !== "undefined") {
                params[param].push(value);
            } else {
                params[param] = value;
            }
        });
        return params;
    }
};
});
