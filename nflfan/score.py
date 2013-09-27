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
    ids = [p.player_id for p in players if p.player_id is not None]
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

    def is_defense(player):
        return player.player_id is None

    def player_query(ids):
        q = nfldb.Query(db)
        q.game(season_year=season, season_type=phase, week=week)
        q.player(player_id=ids)
        return q

    def play_players(ids):
        d = defaultdict(list)
        for pp in player_query(ids).as_play_players():
            d[pp.player_id].append(pp)
        return d

    def def_play_players(team):
        q = nfldb.Query(db)
        q.game(season_year=season, season_type=phase, week=week)

        # Tricky. Throw out all *plays* where `team` did not have possession
        # (they're on defense), but only accept *player* statistics from
        # players on the given team.
        q.play(pos_team__ne=team, team=team)
        return q.as_play_players()

    def playing_statuses():
        q = nfldb.Query(db)
        q.game(season_year=season, season_type=phase, week=week)

        game_status = defaultdict(bool)
        for game in q.as_games():
            playing = game.is_playing
            game_status[game.home_team] = playing
            game_status[game.away_team] = playing
        return game_status

    def tag(statuses, pps, rplayer):
        if is_defense(rplayer):
            pts = _score_defense_team(schema, def_play_players(rplayer.team))
        else:
            pts = _score_player(schema, pps[rplayer.player_id])
        playing = statuses[rplayer.team]
        return rplayer._replace(playing=playing, points=pts)

    pids = [p.player_id for p in players if not is_defense(p)]
    pps = play_players(pids)
    statuses = playing_statuses()
    return map(functools.partial(tag, statuses, pps), players)


def _score_defense_team(schema, pps):
    """
    Given a list of `nfldb.PlayPlayer` objects corresponding to
    defensive plays for a particular team, return the total fantasy
    points in the list according to the `nflfan.ScoreSchema` given.
    """
    s = 0.0
    stats = lambda pp: _pp_stats(pp, _is_defense_stat)
    for cat, v in itertools.chain(*map(stats, pps)):
        s += schema.settings.get(cat, 0.0) * v
    return s


def _score_player(schema, pps):
    """
    Given a list of `nfldb.PlayPlayer` objects, return the total
    fantasy points in the list according to the `nflfan.ScoreSchema`
    given.
    """
    def pick_fg_setting(prefix, yds):
        match_fg = re.compile('%s_([0-9]+)_([0-9]+)' % prefix)
        for cat, point_val in schema.settings.items():
            m = match_fg.match(cat)
            if not m:
                continue
            start, end = int(m.group(1)), int(m.group(2))
            if start <= yds <= end:
                return point_val
        return 0.0

    s = 0.0
    stats = lambda pp: _pp_stats(pp, lambda cat: not _is_defense_stat(cat))
    for cat, v in itertools.chain(*map(stats, pps)):
        if cat == 'kicking_fgm_yds':
            s += pick_fg_setting('kicking_fgm', v)
        if cat == 'kicking_fgmissed_yds':
            s += pick_fg_setting('kicking_fgmissed', v)
        else:
            s += v * schema.settings.get(cat, 0.0)
    return s


def _pp_stats(pp, predicate=None):
    for cat in nfldb.stat_categories:
        if predicate is not None and not predicate(cat):
            continue
        v = getattr(pp, cat, None)
        if v is not None and v != 0:
            yield (cat, float(v))


def _is_defense_stat(name):
    return name.startswith('defense_')


class ScoreSchema (namedtuple('ScoreSchema', 'name settings')):
    __pdoc__['ScoreSchema.name'] = \
        """The name given to this schema in the configuration."""

    __pdoc__['ScoreSchema.settings'] = \
        """
        A dictionary mapping a scoring category to its point value. The
        interpretation of the point value depends on the scoring
        category.
        """
