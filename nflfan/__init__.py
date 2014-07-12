"""
Module nflfan provides a way to connect your fantasy rosters with
statistical data in nfldb in order to perform live scoring. nflfan also
provides a simple web interface that can be used to watch all of your
fantasy games with real time updates. The web server can be started by
running:

    #!bash
    python -m nflfan.web

Currently, only Yahoo and ESPN fantasy leagues are supported. But
nflfan is extensible, and it will be easy to add more leagues in the
future.
"""
from nflfan.config import builtin_providers, load_config, cache_path
from nflfan.provider import __pdoc__ as __provider_pdoc__
from nflfan.provider import player_search
from nflfan.provider import League
from nflfan.provider import Matchup, Owner, Roster, RosterPlayer
from nflfan.provider import Provider, Yahoo, ESPN
from nflfan.score import __pdoc__ as __score_pdoc__
from nflfan.score import score_details, score_roster, score_players
from nflfan.score import tag_players
from nflfan.score import ScoreSchema

__pdoc__ = {}
__pdoc__ = dict(__pdoc__, **__provider_pdoc__)
__pdoc__ = dict(__pdoc__, **__score_pdoc__)

__all__ = [
    # nflfan.config
    'builtin_providers', 'load_config', 'cache_path',

    # nflfan.provider
    'player_search',
    'League',
    'Matchup', 'Owner', 'Roster', 'RosterPlayer',
    'Provider', 'Yahoo', 'ESPN',

    # nflfan.score
    'score_details', 'score_roster', 'score_players', 'tag_players',
    'ScoreSchema',
]
