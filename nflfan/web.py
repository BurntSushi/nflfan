from __future__ import absolute_import, division, print_function
import os.path as path
import time
import urllib

import nfldb

import bottle

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
def v_home():
    return template('home', title='wat')


@bottle.get('/<week:int>')
def v_week(week):
    return template('home')


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
        q = kwargs.pop('qstr', [])
        return (bottle.get_url(rname, **kwargs) + '?' + q).rstrip('?')

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

    bottle.install(exec_time)
    bottle.run()

    db.close()
