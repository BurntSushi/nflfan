from __future__ import absolute_import, division, print_function
from collections import namedtuple

import nfldb

__pdoc__ = {}


def score_roster(schema, roster, phase=nfldb.Enums.season_phase.Regular):
    """
    Given a `nflfan.ScoreSchema` and a `nflfan.Roster`, return a
    new `nflfan.Roster` with a list of `nflfan.Scored` objects
    containing the fantasy points of every player in the roster for the
    corresponding week of football.

    `phase` may be set to a different phase of the season, but
    traditional fantasy sports are only played during the regular
    season, which is the default.
    """
    scored = score_players(schema, roster.players, phase=phase)
    return roster._replace(players=scored)


def score_players(schema, players, phase=nfldb.Enums.season_phase.Regular):
    """
    Given a `nflfan.ScoreSchema`, a list of `nflfan.RosterPlayer`
    and the season year and week of a game, return a list of new
    `nflfan.RosterPlayer` objects with the `playing` and `points`
    attributes set.

    `phase` may be set to a different phase of the season, but
    traditional fantasy sports are only played during the regular
    season, which is the default.

    N.B. `players` is a list because of performance reasons. Namely,
    scoring can use fewer SQL queries when given a collection of players
    to score as opposed to a single player.
    """
    return [p._replace(playing=False, points=0.0) for p in players]


class ScoreSchema (namedtuple('ScoreSchema', 'name settings')):
    __pdoc__['ScoreSchema.name'] = \
        """The name given to this schema in the configuration."""

    __pdoc__['ScoreSchema.settings'] = \
        """
        A dictionary mapping a scoring category to its point value. The
        interpretation of the point value depends on the scoring
        category.
        """
