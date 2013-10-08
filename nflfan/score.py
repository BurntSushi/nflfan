from __future__ import absolute_import, division, print_function
from collections import defaultdict, namedtuple
import functools
import itertools
import re

import nfldb

__pdoc__ = {}


def tag_players(db, players):
    """
    Given a list of `nflfan.RosterPlayer` objects, set the
    `nflfan.RosterPlayer.player` attribute to its corresponding
    `nfldb.Player` object. (Except for roster players corresponding to
    an entire team, e.g., a defense.)
    """
    ids = [p.player_id for p in players if p.is_player]
    q = nfldb.Query(db).player(player_id=ids)
    dbps = dict([(p.player_id, p) for p in q.as_players()])
    return [p._replace(player=dbps.get(p.player_id, None)) for p in players]


def score_roster(db, schema, roster, phase=nfldb.Enums.season_phase.Regular):
    """
    Given a database connection, a `nflfan.ScoreSchema` and a
    `nflfan.Roster`, return a new `nflfan.Roster` with a list of
    `nflfan.Scored` objects containing the fantasy points of every
    player in the roster for the corresponding week of football.

    `phase` may be set to a different phase of the season, but
    traditional fantasy sports are only played during the regular
    season, which is the default.

    Each `nflfan.RosterPlayer` in the roster given will also have the
    `nflfan.RosterPlayer.player` attribute set to its corresponding
    `nfldb.Player` object. (Except for roster players corresponding to
    an entire team, e.g., a defense.)
    """
    tagged = tag_players(db, roster.players)
    scored = score_players(db, schema, tagged, phase=phase)
    return roster._replace(players=scored)


def score_players(db, schema, players, phase=nfldb.Enums.season_phase.Regular):
    """
    Given a database connection, a `nflfan.ScoreSchema`, a list of
    `nflfan.RosterPlayer` and the season year and week of a game,
    return a list of new `nflfan.RosterPlayer` objects with the
    `playing` and `points` attributes set.

    `phase` may be set to a different phase of the season, but
    traditional fantasy sports are only played during the regular
    season, which is the default.

    N.B. `players` is a list because of performance reasons. Namely,
    scoring can use fewer SQL queries when given a collection of players
    to score as opposed to a single player.
    """
    if len(players) == 0:
        return []
    season, week = players[0].season, players[0].week

    def player_query(ids):
        return _game_query(db, players[0], phase=phase).player(player_id=ids)

    def week_games():
        q = _game_query(db, players[0], phase=phase)

        games = {}
        for game in q.as_games():
            games[game.home_team] = game
            games[game.away_team] = game
        return games

    def tag(games, pps, fgs, rp):
        if rp.is_empty:
            return rp

        game = games.get(rp.team, None)
        if rp.is_defense:
            pts = _score_defense_team(schema, db, game, rp, phase)
        else:
            pts = _score_player(schema, pps.get(rp.player_id, None), fgs=fgs)
        return rp._replace(game=game, points=pts)

    games = week_games()
    pids = [p.player_id for p in players if p.is_player]
    fgs = _pp_field_goals(db, players, phase=phase)
    pps = dict([(p.player_id, p) for p in player_query(pids).as_aggregate()])
    return map(functools.partial(tag, games, pps, fgs), players)


def _score_defense_team(schema, db, game, rplayer,
                        phase=nfldb.Enums.season_phase.Regular):
    """
    Given a defensive `nflfan.RosterPlayer`, a nfldb database
    connection and a `nflfan.ScoreSchema`, return the total defensive
    fantasy points for the team.
    """
    assert rplayer.is_defense
    if game is None:
        return 0.0

    q = _game_query(db, rplayer, phase=phase)
    q.play(team=rplayer.team)
    teampps = q.as_aggregate()
    if len(teampps) == 0:
        return 0.0

    s = 0.0
    stats = lambda pp: _pp_stats(pp, _is_defense_stat)
    for cat, v in itertools.chain(*map(stats, teampps)):
        s += schema.settings.get(cat, 0.0) * v

    pa = _defense_points_allowed(schema, db, game, rplayer, phase=phase)
    s += schema._pick_range_setting('defense_pa', pa)
    return s


def _defense_points_allowed(schema, db, game, rplayer,
                            phase=nfldb.Enums.season_phase.Regular):
    """
    Return the total number of points allowed by a defensive team
    `nflfan.RosterPlayer`.
    """
    assert rplayer.is_defense
    assert game is not None

    if rplayer.team == game.home_team:
        pa = game.away_score
    else:
        pa = game.home_score
    if schema.settings.get('defense_pa_style', '') == 'yahoo':
        # It is simpler to think of PA in this case as subtracting certain
        # point allocations from the total scored. More details here:
        # http://goo.gl/t5YMFC
        #
        # Only get the player stats for defensive plays on the opposing
        # side. Namely, the only points not in PA are points scored against
        # rplayer's offensive unit.
        fg_blk_tds = nfldb.Query(db)
        fg_blk_tds.play(defense_misc_tds=1, kicking_fga=1)
        notcount = nfldb.QueryOR(db)
        notcount.play(defense_safe=1, defense_int_tds=1, defense_frec_tds=1)
        notcount.orelse(fg_blk_tds)

        q = _game_query(db, rplayer, phase=phase)
        q.play(gsis_id=game.gsis_id, team__ne=rplayer.team)
        q.andalso(notcount)
        for pp in q.as_aggregate():
            pa -= 2 * pp.defense_safe
            pa -= 6 * pp.defense_int_tds
            pa -= 6 * pp.defense_frec_tds
            pa -= 6 * pp.defense_misc_tds
    return pa


def _score_player(schema, pp, fgs={}):
    """
    Given a `nfldb.PlayPlayer` object, return the total fantasy points
    according to the `nflfan.ScoreSchema` given.

    `fgs` should be a dictionary mapping player id to a list of
    `nfldb.PlayPlayer`, where each describes a *single* field goal
    `attempt.
    """
    if not pp:
        return 0.0

    s = 0.0
    for cat, v in _pp_stats(pp, lambda cat: not _is_defense_stat(cat)):
        s += v * schema.settings.get(cat, 0.0)
    for field, pts, start, end in schema._bonuses():
        if start <= getattr(pp, field, 0.0) <= end:
            s += pts
    for pp in fgs.get(pp.player_id, []):
        for cat, v in _pp_stats(pp, lambda cat: cat.startswith('kicking_fg')):
            if cat == 'kicking_fgm_yds':
                s += schema._pick_range_setting('kicking_fgm', v)
            if cat == 'kicking_fgmissed_yds':
                s += schema._pick_range_setting('kicking_fgmissed', v)
    return s


def _pp_field_goals(db, rplayers, phase=nfldb.Enums.season_phase.Regular):
    """
    Given a nfldb connection and a list of `nflfan.RosterPlayer` objects,
    return a dictionary mapping player id to a list of `nfldb.PlaPlayer`,
    where each describes a *single* field goal attempt.

    This dictionary can be passed to `nflfan._score_player`.
    """
    if len(rplayers) == 0:
        return {}
    q = _game_query(db, rplayers[0], phase=phase).play(kicking_fga=1)
    d = defaultdict(list)
    for pp in q.as_play_players():
        d[pp.player_id].append(pp)
    return d


def _pp_stats(pp, predicate=None):
    for cat in pp.fields:
        if predicate is not None and not predicate(cat):
            continue
        yield (cat, float(getattr(pp, cat)))


def _is_defense_stat(name):
    return name.startswith('defense_')


def _game_query(db, rp, phase=nfldb.Enums.season_phase.Regular):
    q = nfldb.Query(db)
    return q.game(season_year=rp.season, season_type=phase, week=rp.week)


class ScoreSchema (namedtuple('ScoreSchema', 'name settings')):
    __pdoc__['ScoreSchema.name'] = \
        """The name given to this schema in the configuration."""

    __pdoc__['ScoreSchema.settings'] = \
        """
        A dictionary mapping a scoring category to its point value. The
        interpretation of the point value depends on the scoring
        category.
        """

    def _pick_range_setting(self, prefix, v):
        match = re.compile('%s_([0-9]+)_([0-9]+)' % prefix)
        for cat, point_val in self.settings.items():
            m = match.match(cat)
            if not m:
                continue
            start, end = int(m.group(1)), int(m.group(2))
            if start <= v <= end:
                return point_val
        return 0.0

    def _bonuses(self):
        match = re.compile('^bonus_(.+)_([0-9]+)_([0-9]+)$')
        for cat, pts in self.settings.items():
            m = match.match(cat)
            if not m:
                continue
            field, start, end = m.group(1), int(m.group(2)), int(m.group(3))
            yield field, pts, start, end
