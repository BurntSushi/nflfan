from nflfan.config import config
from nflfan.provider import __pdoc__ as __provider_pdoc__
from nflfan.provider import player_search
from nflfan.provider import Matchup, Owner, Roster, RosterPlayer, PositionGroup
from nflfan.provider import Provider, Yahoo, ESPN
from nflfan.score import __pdoc__ as __score_pdoc__
from nflfan.score import score_roster, score_player
from nflfan.score import ScoreSchema, Scored

__pdoc__ = {}
__pdoc__ = dict(__pdoc__, **__provider_pdoc__)
__pdoc__ = dict(__pdoc__, **__score_pdoc__)

__all__ = [
    # nflfan.config
    'config',

    # nflfan.provider
    'player_search',
    'Matchup', 'Owner', 'Roster', 'RosterPlayer', 'PositionGroup',
    'Provider', 'Yahoo', 'ESPN',

    # nflfan.score
    'score_roster', 'score_player',
    'ScoreSchema', 'Scored',
]
