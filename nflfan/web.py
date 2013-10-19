from __future__ import absolute_import, division, print_function
import os.path as path
import random
import re
import time
import urllib

import bottle

import nfldb

import nflvid.vlc

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


@bottle.get('/vid/<gsis_id:int>/<play_id:int>')
def static_vid(gsis_id, play_id):
    if conf.get('video_local', False):
        bottle.abort(500, "Only local video playing is supported.")

    pbp_path = conf.get('footage_pbp_path', '')
    play_path = nflvid.footage_play(pbp_path, str(gsis_id), play_id)
    if play_path is None:
        bottle.abort(404, "Play video not found.")
    fpath, fname = path.split(play_path)
    return bottle.static_file(fname, root=fpath)


@bottle.get('/watch/<gsis_id>/<play_id>', name='watch')
def v_watch(gsis_id, play_id):
    if not conf.get('video_local', False):
        bottle.abort(500, "Local video player disabled.")

    q = nfldb.Query(db)
    plays = q.play(gsis_id=gsis_id, play_id=play_id).as_plays()
    if len(plays) == 0:
        bottle.abort(404, "Play not found.")

    pbp_path = conf.get('footage_pbp_path', '')
    nflvid.vlc.watch(db, plays, footage_play_dir=pbp_path)
    return 'success'


@bottle.get('/', name='week')
def v_week():
    week = get_week()
    games = get_games(week)

    if not query().getall('tags'):
        bottle.request.query['tags'] = 'started'
    if not qget('limit'):
        bottle.request.query['limit'] = 1000000

    auto_update = any(g.is_playing for g in games.values())
    lgs, rosters = my_lg_rosters(week)
    return template('week', games=games, week=week, leagues=lgs,
                    auto_update=auto_update,
                    rosters=rosters, plays=plays_from_tags(week, rosters))


@bottle.get('/plays', name='plays')
def v_plays():
    week = get_week()
    games = get_games(week)
    lgs, rosters = my_lg_rosters(week)

    def show(gid):
        return games[gid].finished or games[gid].is_playing

    game_order = filter(show, list(set(g.gsis_id for g in games.values())))
    game_order = sorted(game_order,
                        key=lambda gid: (not games[gid].is_playing, gid))
    game_plays = {}

    for gid in game_order:
        bottle.request.query.replace('tag_games', gid)
        game_plays[gid] = plays_from_tags(week, rosters)
    bottle.request.query.pop('tag_games', None)

    if not qget('limit'):
        bottle.request.query['limit'] = 10
    bottle.request.query['is_game'] = '1'

    return template('plays', week=week, rosters=rosters,
                    games=games, game_plays=game_plays, game_order=game_order,
                    plays=plays_from_tags(week, rosters))


@bottle.get('/details/<prov>/<league>/<player_id>', name='details')
def vbit_details(prov, league, player_id):
    if prov not in conf['leagues']:
        bottle.abort(404, "Provider %s does not exist." % prov)
    if league not in conf['leagues'][prov]:
        bottle.abort(404, "League %s does not exist in provider %s."
                          % (league, prov))
    week = get_week()
    lg = conf['leagues'][prov][league]
    mine = lg.me(lg.rosters(week))
    if mine is None:
        bottle.abort(404, 'No leagues belonging to you.')

    q = nfldb.Query(db)
    q.game(season_year=season_year, season_type=season_type, week=week)
    pp = q.play(player_id=player_id).as_aggregate()
    if not pp:
        bottle.abort(404, "No stats found for player.")
    pp = pp[0]

    q = nfldb.Query(db)
    q.game(season_year=season_year, season_type=season_type, week=week)
    pp_fgs = q.play(player_id=player_id, kicking_fga=1).as_play_players()

    details = nflfan.score_details(lg.scoring, pp, pp_fgs)
    return template('details', details=details)


@bottle.get('/play-table', name='play-table')
def vbit_play_table():
    week = get_week()
    games = get_games(week)
    lgs, rosters = my_lg_rosters(week)

    return template('play_table', games=games, week=week, rosters=rosters,
                    plays=plays_from_tags(week, rosters))


@bottle.get('/roster/<prov>/<league>', name='roster')
def vbit_roster(prov, league):
    if prov not in conf['leagues']:
        bottle.abort(404, "Provider %s does not exist." % prov)
    if league not in conf['leagues'][prov]:
        bottle.abort(404, "League %s does not exist in provider %s."
                          % (league, prov))
    week = get_week()
    _, _, cweek = nfldb.current(db)
    auto_update = week == cweek

    lg = conf['leagues'][prov][league]
    mine = lg.me(lg.rosters(week))
    if mine is None:
        bottle.abort(404, 'No leagues belonging to you.')

    roster = nflfan.score_roster(db, lg.scoring, mine)
    return template('roster', league=lg, roster=roster,
                    auto_update=auto_update)


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
    return template('league', league=conf['leagues'][prov][league])


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


def plays_from_tags(week, rosters):
    tags = bottle.request.query.getall('tags')
    tag_games = bottle.request.query.getall('tag_games')
    tag_players = bottle.request.query.getall('tag_players')
    started, benched = player_ids(rosters)

    tag_games = filter(lambda x: x, tag_games)
    tag_players = filter(lambda x: x, tag_players)

    q = nfldb.Query(db)
    q.game(season_year=rosters[0].season, season_type=season_type, week=week)
    q.sort(['time_inserted', 'drive_id', 'play_id'])

    if tag_players:
        q.play(player_id=tag_players)
    elif len(rosters) > 0:
        if 'started' in tags:
            q.play(player_id=list(started))
        elif 'bench' in tags:
            q.play(player_id=list(benched))
    if tag_games:
        q.game(gsis_id=tag_games)
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
        qt = lambda s: urllib.quote(str(s))
        return '&'.join('%s=%s' % (qt(k), qt(v)) for k, v in q.items() if v)


@builtin
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


@builtin
def play_video_exists(p):
    if conf.get('footage_pbp_url', ''):
        return True  # This sucks. But what are we to do?
    pbp_path = conf.get('footage_pbp_path', '')
    return nflvid.footage_play(pbp_path, p.gsis_id, p.play_id) is not None


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
           % (g.away_team, g.away_score, g.home_team, g.home_score)


@builtin
def play_context(p):
    down = ''
    if p.down > 0:
        down_str = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th'}
        down = ', %s and %d' % (down_str[p.down], p.yards_to_go)
    return '%s%s' % (p.time, down)


@builtin
def player_ids(rosters):
    start_ids, bench_ids = set(), set()
    for r in rosters:
        for rp in r.players:
            if rp.is_player:
                if rp.bench:
                    bench_ids.add(rp.player_id)
                else:
                    start_ids.add(rp.player_id)
    return start_ids, bench_ids


@builtin
def players_from_rosters(rosters):
    players = {}
    for r in rosters:
        for rp in r.players:
            if rp.is_player:
                players[rp.player.player_id] = rp.player
    return players.values()


@builtin
def players_in_games(gids):
    if not gids:
        return []
    q = nfldb.Query(db)
    q.game(gsis_id=gids)
    return q.as_players()


@builtin
def clean_play_desc(desc):
    desc = re.sub('^\([0-9]+:[0-9]+\)\s+', '', desc)
    desc = re.sub('^\([a-zA-Z]+\)\s+', '', desc)
    return desc.strip()


@builtin
def incl(*args, **kwargs):
    return template(*args, **kwargs)


@builtin
def genid(prefix):
    rands = map(lambda _: str(random.randint(1, 20)), xrange(10))
    return '%s_%s' % (prefix, ''.join(rands))


def conf_leagues(conf):
    for leagues in conf['leagues'].values():
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
    bottle.run(server='paste', host='0.0.0.0', port=8090)

    db.close()
