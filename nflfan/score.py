from __future__ import absolute_import, division, print_function
from collections import namedtuple

import nfldb

import nflfan.provider as provider

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
    scored = []
    for rp in roster.players:
        s = score_player(schema, rp, roster.season, roster.week, phase=phase)
        scored.append(s)

    r = roster
    return provider.Roster(r.provider, r.owner, r.season, r.week, scored)


def score_player(schema, player, season, week,
                 phase=nfldb.Enums.season_phase.Regular):
    """
    Given a `nflfan.ScoreSchema`, a `nflfan.RosterPlayer` and the
    season year and week of a game, return a `nflfan.Scored` object
    containing the roster player and the number of fantasy points
    scored by the player in the given week.

    `phase` may be set to a different phase of the season, but
    traditional fantasy sports are only played during the regular
    season, which is the default.
    """
    return Scored(player, season, week, 0.0)


class ScoreSchema (namedtuple('ScoreSchema', 'name settings')):
    __pdoc__['ScoreSchema.name'] = \
        """The name given to this schema in the configuration."""

    __pdoc__['ScoreSchema.settings'] = \
        """
        A dictionary mapping a scoring category to its point value. The
        interpretation of the point value depends on the scoring
        category.
        """


class Scored (namedtuple('Scored', 'rplayer season week points')):
    def __getattr__(self, k):
        # WTF. Basically, I want to express `Scored` as an extension of
        # the `RosterPlayer` product type. Normally I'd just subclass,
        # but I'm not sure how to do it with namedtuples.
        return getattr(self.rplayer, k)

    def __str__(self):
        return '%-6s %-4s %0.2f pts %s (%s)' \
               % (self.position, self.team, self.points, self.name,
                  self.group.name)
