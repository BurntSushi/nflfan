from __future__ import absolute_import, division, print_function
import os.path as path
import re
import time
import urllib

import bottle

import nfldb

# import nflvid.vlc 

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

season_year = None
"""The current season."""

season_type = 'Regular'
"""The current phase of the season."""

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


@bottle.get('/watch/<gsis_id>/<play_id>', name='watch')
def v_watch(gsis_id, play_id):
    q = nfldb.Query(db)
    plays = q.play(gsis_id=gsis_id, play_id=play_id).as_plays()
    if len(plays) == 0:
        bottle.abort(404, "Play not found.")

    # nflvid.vlc.watch(db, [plays[0]]) 
    return 'success'

@bottle.get('/')
def v_week():
    week = get_week()
    games = get_games(week)

    lgs, rosters = my_lg_rosters(week)
    plays = plays_from_rosters(rosters)

    if not query().getall('tags'):
        bottle.request.query['tags'] = 'mine'
    if not qget('limit'):
        bottle.request.query['limit'] = 1000000

    return template('week', games=games, week=week, plays=plays,
                    leagues=lgs, rosters=rosters)

@bottle.get('/plays')
def v_plays():
    week = get_week()
    games = get_games(week)
    lgs, rosters = my_lg_rosters(week)

    q = nfldb.Query(db)
    q.game(season_year=rosters[0].season, season_type=season_type,
           week=rosters[0].week)
    q.sort(['time_inserted', 'drive_id', 'play_id'])
    plays = q.as_plays(fill=True)

    return template('plays', games=games, week=week, plays=plays,
                    rosters=rosters)


@bottle.get('/play-table')
def vbit_play_table():
    week = get_week()
    games = get_games(week)
    lgs, rosters = my_lg_rosters(week)

    q = nfldb.Query(db)
    q.game(season_year=rosters[0].season, season_type=season_type,
           week=rosters[0].week)
    q.sort(['time_inserted', 'drive_id', 'play_id'])
    plays = q.as_plays(fill=True)

    return template('play_table', games=games, week=week, plays=plays,
                    rosters=rosters)


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


@bottle.error(500)
def v_500(error):
    message = str(getattr(error, 'exception', 'Unknown error.'))
    return template('error_500', message=message, notime=True)


def get_games(week):
    q = nfldb.Query(db)
    q.game(season_year=season_year, season_type=season_type, week=week)
    d = {}
    for g in q.as_games():
        d[g.gsis_id] = g
        d[g.home_team] = g
        d[g.away_team] = g
    return d


def get_week():
    if 'week' not in bottle.request.query:
        _, _, week = nfldb.current(db)
        return week
    week_str = bottle.request.query['week']
    try:
        week = int(week_str)
        if week < 1 or week > 25:
            bottle.abort(404, "Invalid week %d" % week)
        return week
    except ValueError:
        bottle.abort(404, "Week %s is not an integer." % week_str)


def my_lg_rosters(week):
    lgs, rosters = [], []
    for lg in conf_leagues(conf):
        mine = lg.me(lg.rosters(week))
        if mine is None:
            continue
        mine = nflfan.score_roster(db, lg.scoring, mine)
        lgs.append(lg)
        rosters.append(mine)
    return lgs, rosters


def plays_from_rosters(rosters):
    if len(rosters) == 0:
        return []

    _, ids = player_ids(rosters)
    q = nfldb.Query(db)
    q.game(season_year=rosters[0].season, season_type=season_type,
           week=rosters[0].week)
    q.play(player_id=list(ids))
    q.sort(['time_inserted', 'drive_id', 'play_id'])
    return q.as_plays(fill=True)


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

    @staticmethod
    def play(p):
        return url.fresh('watch', gsis_id=p.gsis_id, play_id=p.play_id)


@builtin
def qget(field, default=None):
    return bottle.request.query.get(field, default)


@builtin
def query():
    return bottle.request.query


@builtin
def game_str(games, id_or_team):
    g = games.get(id_or_team, None)
    if g is None:
        return 'Unknown game'
    return '%s (%d) at %s (%d)' \
           % (g.home_team, g.home_score, g.away_team, g.away_score)


@builtin
def player_ids(rosters):
    defenses, ids = set(), set()
    for r in rosters:
        for rp in r.players:
            if rp.is_player:
                ids.add(rp.player_id)
            elif rp.is_defense:
                defenses.add(rp.team)
    return defenses, ids


@builtin
def clean_play_desc(desc):
    desc = re.sub('^\([0-9]+:[0-9]+\)\s+', '', desc)
    desc = re.sub('^\([a-zA-Z]+\)\s+', '', desc)
    return desc.strip()


@builtin
def incl(*args, **kwargs):
    return template(*args, **kwargs)


def conf_leagues(conf):
    for leagues in conf.values():
        for lg in leagues.values():
            yield lg


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

    _, season_year, _ = nfldb.current(db)

    builtins['db'] = db
    builtins['conf'] = conf

    bottle.install(exec_time)
    bottle.run(host='0.0.0.0', port=8090)

    db.close()
