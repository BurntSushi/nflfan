from __future__ import absolute_import, division, print_function

import itertools
import json
import os.path as path
import time

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
#
# TODO: I think psycopg2 has a connection pool feature. Use it.
db = None
"""A global database connection."""

web_path = path.join(path.split(__file__)[0], 'web')
"""The absolute path of the directory containing web assets."""

builtins = {}
"""An environment of builtin functions passed to every template."""


@bottle.get('/seasons/<season:int>/phases/<phase>'
            '/weeks/<week:int>/games',
            name='v_games')
def v_games(season, phase, week):
    phase = as_phase(phase)
    q = nfldb_sort(nfldb.Query(db))
    games = q.game(season_year=season, season_type=phase, week=week).as_games()
    return template('games', season=season, phase=phase, week=week,
                    games=games)


@bottle.get('/css/<name:path>')
def static_css(name):
    return bottle.static_file(name, root=path.join(web_path, 'css'))


@bottle.get('/js/<name:path>')
def static_js(name):
    return bottle.static_file(name, root=path.join(web_path, 'js'))


@bottle.get('/fonts/<name:path>')
def static_fonts(name):
    return bottle.static_file(name, root=path.join(web_path, 'fonts'))


@bottle.get('/favicon.ico')
def v_favicon():
    bottle.abort(404, "No favicon")


def rest(f):
    def _(*args, **kwargs):
        bottle.response.content_type = 'application/json'
        return json.dumps(f(*args, **kwargs), indent=2)
    return _


@bottle.get('/v1/current', name='v1_current')
@rest
def rest_current():
    phase, season, week = nfldb.current(db)
    return {'phase': str(phase), 'season': season, 'week': week}


@bottle.get('/v1/seasons', name='v1_seasons')
@rest
def rest_seasons():
    return range(2009, 2015)


@bottle.get('/v1/seasons/<season:int>/phases', name='v1_phases')
@rest
def rest_phases(season):
    return ['Preseason', 'Regular', 'Postseason']


@bottle.get('/v1/seasons/<season:int>/phases/<phase>/weeks', name='v1_weeks')
@bottle.get('/v1/leagues/<lg>/weeks', name='v1_league_weeks')
@rest
def rest_weeks(season=None, phase=None, lg=None):
    if lg is not None:
        lg = league(lg)
        return rest_weeks(season=lg.season, phase=lg.phase)

    phase = as_phase(phase)
    if phase == nfldb.Enums.season_phase.Preseason:
        return range(1, 5)
    elif phase == nfldb.Enums.season_phase.Regular:
        return range(1, 18)
    elif phase == nfldb.Enums.season_phase.Postseason:
        return range(1, 5)
    else:
        assert False, 'unreachable'


@bottle.get('/v1/seasons/<season:int>/phases/<phase>'
            '/weeks/<week:int>/games',
            name='v1_games')
@bottle.get('/v1/games/<gsis_id>', name='v1_game')
@rest
def rest_games(season=None, phase=None, week=None, gsis_id=None):
    if gsis_id is None:
        q = nfldb.Query(db)
        q.game(season_year=season, season_type=as_phase(phase), week=week)
        return map(as_rest_game, nfldb_sort(q).as_games())
    else:
        return as_rest_game(nfldb.Game.from_id(db, gsis_id))


@bottle.get('/v1/games/<gsis_id>/drives', name='v1_drives')
@bottle.get('/v1/games/<gsis_id>/drives/<drive_id>', name='v1_drive')
@rest
def rest_drives(gsis_id, drive_id=None):
    if drive_id is None:
        q = nfldb.Query(db)
        q.game(gsis_id=gsis_id)
        return map(as_rest_drive, q.sort(('drive_id', 'asc')).as_drives())
    else:
        return as_rest_drive(nfldb.Drive.from_id(db, gsis_id, drive_id))


@bottle.get('/v1/seasons/<season:int>/phases/<phase>/weeks/<week:int>/plays',
            name='v1_week_plays')
@bottle.get('/v1/games/<gsis_id>/plays', name='v1_plays')
@bottle.get('/v1/games/<gsis_id>/drives/<drive_id>/plays',
            name='v1_drive_plays')
@bottle.get('/v1/games/<gsis_id>/drives/<drive_id>/plays/<play_id>',
            name='v1_drive_play')
@rest
def rest_plays(season=None, phase=None, week=None,
               gsis_id=None, drive_id=None, play_id=None):
    if play_id is None:
        q = nfldb.Query(db)
        if None not in (season, phase, week):
            q.game(season_year=season, season_type=as_phase(phase), week=week)
        if gsis_id is not None:
            q.game(gsis_id=gsis_id)
        if drive_id is not None:
            q.drive(drive_id=drive_id)
        return map(as_rest_play, nfldb_sort(q).as_plays(fill=True))
    else:
        return as_rest_play(nfldb.Play.from_id(db, gsis_id, drive_id, play_id))


@bottle.get('/v1/seasons/<season:int>/phases/<phase>/weeks/<week:int>/players',
            name='v1_week_players')
@bottle.get('/v1/games/<gsis_id>/players', name='v1_game_players')
@rest
def rest_players(season=None, phase=None, week=None, gsis_id=None):
    phase = as_phase(phase)
    q = nfldb.Query(db)
    if None not in (season, phase, week):
        q.game(season_year=season, season_type=phase, week=week)
    if gsis_id is not None:
        q.game(gsis_id=gsis_id)
    return map(as_rest_player, q.sort(('full_name', 'asc')).as_players())


@bottle.get('/v1/players', name='v1_players')
@bottle.get('/v1/players/<player_id>', name='v1_player')
@rest
def rest_player(player_id=None):
    if player_id is None:
        bottle.abort(400, 'Cannot list all players.')
    return as_rest_player(nfldb.Player.from_id(db, player_id))


@bottle.get('/v1/seasons/<season:int>/phases/<phase>/leagues',
            name='v1_season_leagues')
@rest
def rest_season_leagues(season, phase):
    lgs = leagues(season=season, phase=phase)
    return map(as_rest_league, lgs)


@bottle.get('/v1/leagues', name='v1_leagues')
@bottle.get('/v1/leagues/<lg>', name='v1_league')
@rest
def rest_leagues(lg=None):
    if lg is None:
        return map(as_rest_league, leagues())
    else:
        lg = league(lg)
        return as_rest_league(lg)


@bottle.get('/v1/leagues/<lg>/weeks/<week:int>/me', name='v1_me')
@rest
def rest_me(lg, week):
    lg = league(lg)
    if len(lg.conf.get('me', '')) == 0:
        bottle.abort(400, '"me" is not configured for league "%s".'
                          % lg.full_name)
    me_owner = lg.me(lg.owners(week))
    if me_owner is None:
        bottle.abort(404, 'Could not find owner matching "me" value "%s".'
                          % lg.full_name)
    return as_rest_owner(me_owner)


@bottle.get('/v1/leagues/<lg>/weeks/<week:int>/owners', name='v1_owners')
@bottle.get('/v1/leagues/<lg>/weeks/<week:int>/owners/<owner>', name='v1_owner')
@rest
def rest_owners(lg, week, owner=None):
    if owner is None:
        return map(as_rest_owner, league(lg).owners(week))
    else:
        owner = no_none(league(lg).owner(week, owner), 'owner', owner)
        return as_rest_owner(owner)


@bottle.get('/v1/leagues/<lg>/weeks/<week:int>/matchups', name='v1_matchups')
@bottle.get('/v1/leagues/<lg>/weeks/<week:int>/matchups/<matchup>',
            name='v1_matchup')
@rest
def rest_matchups(lg, week, matchup=None):
    if matchup is None:
        return map(as_rest_matchup, league(lg).matchups(week))
    else:
        matchup = no_none(league(lg).matchup(week, matchup),
                          'matchup', matchup)
        return as_rest_matchup(matchup)


@bottle.get('/v1/leagues/<lg>/weeks/<week:int>/rosters',
            name='v1_rosters')
@bottle.get('/v1/leagues/<lg>/weeks/<week:int>/rosters/<roster>',
            name='v1_roster')
@rest
def rest_rosters(lg, week, roster=None):
    if bottle.request.query.get('scored', False):
        score = scored_roster
    else:
        score = lambda _, y: y

    lg = league(lg)
    if roster is None:
        def scored_rest(r):
            return as_rest_roster(score(lg, r))
        return map(scored_rest, lg.rosters(week))
    else:
        roster = no_none(lg.roster(week, roster), 'roster', roster)
        return as_rest_roster(score(lg, roster))


def nfldb_sort(q):
    '''
    Given an `nfldb.Query` object, apply the necessary sorting and
    limit criteria to it from the request parameters.
    '''
    params = bottle.request.query
    limit = param_int('limit', 20)
    sorts = []  # param to pass to nfldb.Query().sort(...)
    for field in params.getall('sort'):
        if len(field) == 0:
            continue
        if field[0] == '-':
            sorts.append((field[1:], 'desc'))
        else:
            if field[0] == '+':
                field = field[1:]
            sorts.append((field, 'asc'))
    return q.sort(sorts).limit(limit)


def as_rest_league(lg):
    return {
        'season': lg.season,
        'phase': str(lg.phase),
        'ident': lg.ident,
        'prov_name': lg.prov_name,
        'name': lg.name,
        'scoring_schema': lg.scoring.name,
    }


def as_rest_owner(o):
    return { 'ident': o.ident, 'name': o.name }


def as_rest_matchup(m):
    return {
        'owner1': as_rest_owner(m.owner1),
        'owner2': as_rest_owner(m.owner2),
    }


def as_rest_roster(r):
    return {
        'owner': as_rest_owner(r.owner),
        'players': map(as_rest_roster_player, r.players),
    }


def as_rest_roster_player(p):
    return {
        'position': p.position,
        'team': p.team,
        'bench': p.bench,
        'season': p.season,
        'week': p.week,
        'gsis_id': p.game.gsis_id if p.game is not None else None,
        'points': p.points,
        'player_id': p.player_id,
    }


def as_rest_game(g):
    return {
        'away_score': g.away_score,
        'away_team': g.away_team,
        'away_turnovers': g.away_turnovers,
        'home_score': g.home_score,
        'home_team': g.home_team,
        'home_turnovers': g.home_turnovers,
        'day_of_week': str(g.day_of_week),
        'finished': g.finished,
        'gamekey': g.gamekey,
        'gsis_id': g.gsis_id,
        'is_playing': g.is_playing,
        'loser': g.loser,
        'winner': g.winner,
        'phase': str(g.season_type),
        'season': g.season_year,
        'start_time': g.start_time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'week': g.week,
    }


def as_rest_drive(d):
    return {
        'drive_id': d.drive_id,
        'start_field': str(d.start_field),
        'end_field': str(d.end_field),
        'start_time': str(d.start_time),
        'end_time': str(d.end_time),
        'first_downs': d.first_downs,
        'gsis_id': d.gsis_id,
        'penalty_yards': d.penalty_yards,
        'play_count': d.play_count,
        'pos_team': d.pos_team,
        'pos_time': str(d.pos_time),
        'result': d.result,
        'yards_gained': d.yards_gained,
    }


def as_rest_play(p):
    d = {
        'description': p.description,
        'down': p.down,
        'play_id': p.play_id,
        'drive_id': p.drive_id,
        'gsis_id': p.gsis_id,
        'note': p.note,
        'points': p.points,
        'pos_team': p.pos_team,
        'scoring_team': p.scoring_team,
        'time': str(p.time),
        'yardline': str(p.yardline),
        'yards_to_go': p.yards_to_go,
        'players': [pp.player_id for pp in p.play_players],
    }
    cats = [k for k, v in nfldb.stat_categories.iteritems()
              if v.category_type == nfldb.Enums.category_scope.play]
    return dict(d, **{cat: getattr(p, cat) for cat in cats})


def as_rest_play_player(p):
    d = {
        'player_id': p.player_id,
        'play_id': p.play_id,
        'drive_id': p.drive_id,
        'gsis_id': p.gsis_id,
        'points': p.points,
        'scoring_team': p.scoring_team,
        'team': p.team,
    }
    cats = [k for k, v in nfldb.stat_categories.iteritems()
              if v.category_type == nfldb.Enums.category_scope.player]
    return dict(d, **{cat: getattr(p, cat) for cat in cats})


def as_rest_player(p):
    return {
        'player_id': p.player_id,
        'birthdate': p.birthdate,
        'college': p.college,
        'first_name': p.first_name,
        'last_name': p.last_name,
        'full_name': p.full_name,
        'gsis_name': p.gsis_name,
        'height': p.height,
        'position': str(p.position),
        'profile_id': p.profile_id,
        'profile_url': p.profile_url,
        'status': str(p.status),
        'team': p.team,
        'uniform_number': p.uniform_number,
        'weight': p.weight,
        'years_pro': p.years_pro,
    }


def as_phase(phase):
    if isinstance(phase, nfldb.Enums.season_phase):
        return phase
    try:
        return nfldb.Enums.season_phase[phase]
    except KeyError:
        bottle.abort(404, "Unknown phase '%s'" % phase)


def no_none(v, thing, key):
    if v is None:
        bottle.abort(400, "Could not find %s with id %s" % (thing, key))
    return v


def scored_roster(lg, roster):
    return nflfan.score_roster(db, lg.scoring, roster, phase=lg.phase)


def league(name):
    lgs = [lgs[name] for lgs in conf['leagues'].itervalues() if name in lgs]
    if len(lgs) == 0:
        bottle.abort(404, "League '%s' not found." % name)
    if len(lgs) >= 2:
        bottle.abort(400, "League identifier '%s' is not unique." % name)
    return lgs[0]


def leagues(season=None, phase=None):
    leagues = []
    if phase is not None:
        phase = as_phase(phase)
    for lgs in conf['leagues'].values():
        for lg in lgs.values():
            if season and lg.season != season:
                continue
            if phase and lg.phase != phase:
                continue
            leagues.append(lg)
    return sorted(leagues, key=lambda lg: (-lg.season, lg.name))


def param_int(name, default=None):
    try:
        return int(bottle.request.query.get(name, default))
    except ValueError:
        return default


def builtin(f):
    builtins[f.__name__] = f
    return f


def template(*args, **kwargs):
    for name, f in builtins.items():
        if name not in kwargs:
            kwargs[name] = f
    return bottle.template(*args, **kwargs)


@builtin
def grouped(n, iterable):
    it = itertools.izip_longest(*([iter(iterable)] * n))
    return ([x for x in xs if x is not None] for xs in it)


def exec_time(cb):
    def _(*args, **kwargs):
        start = time.time()
        r = cb(*args, **kwargs)
        end = time.time()
        # A hack to make the response time available in the template.
        if isinstance(r, strtype):
            r = r.replace('$exec_time$', str(end - start))
        # Show response time on all requests via header.
        bottle.response.headers['X-Exec-Time'] = str(end - start)
        return r
    return _


if __name__ == '__main__':
    bottle.TEMPLATE_PATH.insert(0, path.join(web_path, 'tpl'))
    db = nfldb.connect()
    conf = nflfan.load_config(providers=nflfan.builtin_providers)

    builtins['db'] = db
    builtins['conf'] = conf

    bottle.install(exec_time)
    bottle.run(server='paste', host='0.0.0.0', port=8090, debug=True,
               reloader=True)

    db.close()
