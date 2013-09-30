from __future__ import absolute_import, division, print_function
import os.path as path
import time
import urllib

import bottle

import nfldb

import nflfan

try:
    strtype = basestring
except NameError:
    strtype = str

# I am cheating a bit here by using a single DB connection for all requests.
# The best way to do things is still a bit unclear to me, although I suspect
# it might involve writing a simple Bottle plugin. But then I need a connection
# pool... *sigh*... Hasn't somebody solved this already? Suggestions please!
db = None
"""A global database connection."""

conf = None
"""The nflfan configuration."""

web_path = path.join(path.split(__file__)[0], 'web')
"""The absolute path of the directory containing web assets."""

builtins = {}
"""An environment of builtin functions passed to every template."""


@bottle.get('/css/<name>')
def static_css(name):
    return bottle.static_file(name, root=path.join(web_path, 'css'))


@bottle.get('/js/<name>')
def static_js(name):
    return bottle.static_file(name, root=path.join(web_path, 'js'))


@bottle.get('/')
@bottle.get('/<week:int>')
def v_week(week=None):
    if week is None:
        _, _, week = nfldb.current(db)
    return template('home')


@bottle.get('/<prov>/<league>', name='league')
@bottle.get('/<prov>/<league>/<week:int>', name='league_week')
def v_league(prov, league, week=None):
    if week is None:
        _, _, week = nfldb.current(db)
    if prov not in conf:
        bottle.abort(404, "Provider %s does not exist." % prov)
    if league not in conf[prov]:
        bottle.abort(404, "League %s does not exist in provider %s."
                          % (league, prov))
    return template('league', league=conf[prov][league])


@bottle.error(404)
def v_404(error):
    return template('error_404', message=error.output, notime=True)


def builtin(f):
    builtins[f.__name__] = f
    return f


def template(*args, **kwargs):
    for name, f in builtins.items():
        if name not in kwargs:
            kwargs[name] = f
    return bottle.template(*args, **kwargs)


@builtin
class url (object):  # Evil namespace trick.
    @staticmethod
    def fresh(rname, **kwargs):
        q = kwargs.pop('qstr', '')
        app = bottle.default_app()
        return (app.get_url(rname, **kwargs) + '?' + q).rstrip('?')

    @staticmethod
    def same(**q):
        return (bottle.request.fullpath + '?' + url.qstr(**q)).rstrip('?')

    @staticmethod
    def qstr(**q):
        return url.qstr_fresh(**dict(bottle.request.query, **q))

    @staticmethod
    def qstr_fresh(**q):
        qt = urllib.quote
        return '&'.join('%s=%s' % (qt(k), qt(v)) for k, v in q.items() if v)


def exec_time(cb):
    def _(*args, **kwargs):
        start = time.time()
        r = cb(*args, **kwargs)
        end = time.time()
        if isinstance(r, strtype):
            r = r.replace('$exec_time$', str(end - start))
        return r
    return _

if __name__ == '__main__':
    bottle.TEMPLATE_PATH.insert(0, path.join(web_path, 'html'))
    db = nfldb.connect()
    conf = nflfan.load_config(providers=nflfan.builtin_providers)

    builtins['db'] = db
    builtins['conf'] = conf

    bottle.install(exec_time)
    bottle.run()

    db.close()
