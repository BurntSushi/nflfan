from __future__ import absolute_import, division, print_function
from collections import defaultdict, namedtuple
import functools

import nfldb

__pdoc__ = {}


def score_roster(db, schema, roster, phase=nfldb.Enums.season_phase.Regular):
    """
    Given a database connection, a `nflfan.ScoreSchema` and a
    `nflfan.Roster`, return a new `nflfan.Roster` with a list of
    `nflfan.Scored` objects containing the fantasy points of every
    player in the roster for the corresponding week of football.

    `phase` may be set to a different phase of the season, but
    traditional fantasy sports are only played during the regular
    season, which is the default.
    """
    scored = score_players(db, schema, roster.players, phase=phase)
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
            d[pp.player_id] = pp
        return d

    def def_play_players(team):
        q = nfldb.Query(db)
        q.game(season_year=season, season_type=phase, week=week)

        # Tricky. Throw out all *plays* where `team` did not have possession
        # (they're on defense), but only accept *player* statistics from 
        # players on the given team.
        q.play(pos_team__ne=team, team=team)
        return q.as_play_players()

    def playing_statuses(pps, teams):
        q = nfldb.Query(db)
        q.game(season_year=season, season_type=phase, week=week)

        game_status = {}
        for game in q.as_games():
            playing = game.is_playing
            game_status[game.gsis_id] = playing
            game_status[game.home_team] = playing
            game_status[game.away_team] = playing

        d = defaultdict(bool)
        for ppid, pp in pps.items():
            d[ppid] = game_status[pp.gsis_id]
        for t in teams:
            d[t] = game_status[t]
        return d

    def tag(statuses, pps, rplayer):
        if is_defense(rplayer):
            pts = _score_defense_team(schema, def_play_players(rplayer.team))
        else:
            pts = _score_player(schema, pps[rplayer.player_id])
        playing = statuses[rplayer.id]
        return rplayer._replace(playing=playing, points=pts)

    pids = [p.player_id for p in players if not is_defense(p)]
    tids = [p.team for p in players if is_defense(p)]
    pps = play_players(pids)
    statuses = playing_statuses(pps, tids)
    return map(functools.partial(tag, statuses, pps), players)


def _score_defense_team(schema, pps):
    """
    Given a list of `nfldb.PlayPlayer` objects corresponding to
    defensive plays for a particular team, return the total fantasy
    points in the list according to the `nflfan.ScoreSchema` given.
    """
    return 0.0


def _score_player(schema, pps):
    """
    Given a list of `nfldb.PlayPlayer` objects, return the total
    fantasy points in the list according to the `nflfan.ScoreSchema`
    given.
    """
    return 0.0


class ScoreSchema (namedtuple('ScoreSchema', 'name settings')):
    __pdoc__['ScoreSchema.name'] = \
        """The name given to this schema in the configuration."""

    __pdoc__['ScoreSchema.settings'] = \
        """
        A dictionary mapping a scoring category to its point value. The
        interpretation of the point value depends on the scoring
        category.
        """
