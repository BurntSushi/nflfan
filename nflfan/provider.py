from __future__ import absolute_import, division, print_function
from collections import namedtuple
import functools
import re

import requests

from bs4 import BeautifulSoup

import nfldb

__pdoc__ = {}

_user_agent = 'Mozilla/5.0'

_urls = {
    'yahoo': {
        'owner': 'http://football.fantasysports.yahoo.com/f1/%s/teams',
        'matchup': 'http://football.fantasysports.yahoo.com/f1/%s/'
                   'matchup?matchup_week=%d&ajaxrequest=1',
        'roster': 'http://football.fantasysports.yahoo.com/f1/%s/%s?week=%d',
    },
}


def pp(soup):
    print(soup.prettify().encode('utf-8'))


def player_search(db, full_name, team=None, position=None):
    """
    A thin wrapper around `nfldb.player_search` that tries searching
    with `team` or `position` when given, but if no results are found,
    then this returns the results of a search with just the full name.

    This allows for a slightly out-of-date database to still provide
    a match while also disambiguating players with the same name.
    """
    if position not in nfldb.Enums.player_pos:
        position = None

    p, _ = nfldb.player_search(db, full_name, team=team, position=position)
    if p is None and position is not None:
        p, _ = nfldb.player_search(db, full_name, team=team, position=None)
    if p is None and team is not None:
        p, _ = nfldb.player_search(db, full_name, team=None, position=position)
    if p is None and team is not None and position is not None:
        p, _ = nfldb.player_search(db, full_name, team=None, position=None)
    return p


class Matchup (namedtuple('Matchup', 'owner1 owner2')):
    __pdoc__['Matchup.owner1'] = \
        """
        One of the two teams in this matchup represented as an
        `nflfan.Owner` object.
        """

    __pdoc__['Matchup.owner2'] = \
        """
        One of the two teams in this matchup represented as an
        `nflfan.Owner` object.
        """

    def __str__(self):
        return '%s vs. %s' % (self.owner1, self.owner2)


class Owner (namedtuple('Owner', 'provider ident name')):
    __pdoc__['Owner.provider'] = \
        """The `nflfan.Provider` object that created this owner."""

    __pdoc__['Owner.ident'] = \
        """
        A unique identifier corresponding to this owner. The type
        of this value is provider-dependent.
        """

    __pdoc__['Owner.name'] = \
        """
        A string representing the name of this owner.
        """

    def __str__(self):
        return self.name


class Roster (namedtuple('Roster', 'provider owner season week players')):
    __pdoc__['Roster.provider'] = \
        """The `nflfan.Provider` object that created this roster."""

    __pdoc__['Roster.owner'] = \
        """
        A `nflfan.Owner` object corresponding to the owner of this
        roster.
        """

    __pdoc__['Roster.players'] = \
        """
        A list of `nflfan.RosterPlayer` objects corresponding to the
        set of players on this roster.
        """

    def new_player(self, pos, team, pgroup, bench, player):
        """
        A convenience method for creating a new `nflfan.RosterPlayer`
        given the current roster.
        """
        return RosterPlayer(pos, team, pgroup, bench, self.season, self.week,
                            False, 0.0, player)

    @property
    def active(self):
        return filter(lambda rp: not rp.bench, self.players)

    @property
    def benched(self):
        return filter(lambda rp: rp.bench, self.players)

    def grouped(self, bench=True):
        """
        Returns a list of lists, where each list corresponds to only
        the players in a particular position grouping.

        When `bench` is `False`, then benched players will be omitted.
        """
        rps = sorted(self.players, key=lambda rp: (rp.group, rp.bench))
        groups = []
        g = []
        last = None
        for i, rp in enumerate(rps):
            if i == 0 or last != rp.group:
                groups.append(g)
                g = [rp]
            else:
                g.append(rp)
            last = rp.group
        groups.append(g)
        return groups

    def __str__(self):
        s = []
        for group in self.grouped():
            for rp in group:
                s.append(str(rp))
        return '\n'.join(s)


class RosterPlayer (
    namedtuple('RosterPlayer',
               'position team group bench season week playing points player')):
    __pdoc__['RosterPlayer.position'] = \
        """
        A string corresponding to the position of the roster spot
        occupied by this player. The possible values of this string are
        provider dependent.
        """

    __pdoc__['RosterPlayer.team'] = \
        """
        A team abbreviation that this player belongs to. It must be a
        valid nfldb team abbreviation and *cannot* be `UNK`.
        """

    __pdoc__['RosterPlayer.group'] = \
        """The `nflfan.PositionGroup` that this player belongs to."""

    __pdoc__['RosterPlayer.bench'] = \
        """A boolean indicating whether this is a bench position or not."""

    __pdoc__['Roster.season'] = \
        """The year of the corresponding NFL season."""

    __pdoc__['Roster.week'] = \
        """The week number in which this roster was set."""

    __pdoc__['RosterPlayer.playing'] = \
        """Whether this player is playing in active game or not."""

    __pdoc__['RosterPlayer.points'] = \
        """The total fantasy points for this roster player."""

    __pdoc__['RosterPlayer.player'] = \
        """
        A `nfldb.Player` object corresponding to the player in this
        roster position. This may be `None` when the roster player
        corresponds to an entire team. (e.g., A defense.)
        """

    @property
    def name(self):
        return self.team if self.player is None else self.player.full_name

    def __str__(self):
        return '%-6s %-4s %0.2f %s (%s)' \
               % (self.position, self.team, self.points,
                  self.name, self.group.name)


@functools.total_ordering
class PositionGroup (namedtuple('PositionGroup', 'name fields')):
    """
    Represents a grouping of statistical categories corresponding
    to players at related positions. For example, kickers have
    distinct statistical categories and therefore have their own
    group. Conversely, QBs, RBs, WRs and TEs all have similar
    statistical categories and therefore usually belong to the same
    group.
    """
    _ord = ['offense', 'kicking', 'defense']
    """The order that the position groups should be displayed."""

    __pdoc__['PositionGroup.name'] = \
        """The name for this position group used in the configuration."""

    __pdoc__['PositionGroup.fields'] = \
        """
        An association list mapping display names to statistical
        categories. This list defines the set of columns to show for
        this position grouping.
        """

    def __str__(self):
        print(self.fields)
        cols = ', '.join([disp for disp, _ in self.fields])
        return '%s: %s' % (self.name, cols)

    def __lt__(self, other):
        seq = PositionGroup._ord.index
        return seq(self.name) < seq(other.name)


class Provider (object):
    """
    This class describes the interface that each fantasy football
    provider must implement so that it can work with nflfan. In other
    words, this is an abstract base class that should **not** be
    instantiated directly.

    All public members of this class must also be defined in each
    provider implementation, including the class variables.
    """

    name = None
    """The name of the provider used in the configuration file."""

    conf_required = ['scoring', 'position_groups',
                     'name', 'season', 'league_id']
    """A list of fields required for every provider."""

    conf_optional = []
    """A list of fields that are optional for every provider."""

    def owners(self):
        """Returns a list of `nflfan.Owner` objects."""
        assert False, 'subclass responsibility'

    def matchups(self, week):
        """
        Given a week number, this returns a list of `nflfan.Matchup`
        objects describing the head-to-head matchups for `week`.
        """
        assert False, 'subclass responsibility'

    def roster(self, player_search, owner, week):
        """
        Given a `nflfan.Owner` and a week number, this returns a
        `nflfan.Roster` object. The `nflfan.Roster` contains a list
        of `nfldb.Player` objects, their corresponding position
        on the roster, and the position group that the position
        belongs to.

        `player_search` should be a function that takes a full
        player name and returns the closest matching player as a
        `nfldb.Player` object. It should also optionally take keyword
        arguments `team` and `position` that allow for extra filtering.

        Note that the roster position is a string but the set of
        possible values is provider dependent. It is used for display
        purposes only.
        """
        assert False, 'subclass responsibility'

    def _set_conf_attrs(self, provider, lg):
        for k in Provider.conf_required + Provider.conf_optional:
            setattr(self, k, lg.get(k, None))
        for k in provider.conf_required + provider.conf_optional:
            setattr(self, k, lg.get(k, None))


class Yahoo (Provider):
    name = 'yahoo'
    conf_required = []
    conf_optional = ['username', 'password']
    _headers = {'User-Agent': _user_agent}

    def __init__(self, lg):
        self._set_conf_attrs(Yahoo, lg)
        self.season_id, _, self.league_num = self.league_id.split('.')

        self._session = requests.Session()
        self._session.headers.update(Yahoo._headers)
        self._login()

    def owners(self):
        match_owner_link = re.compile('team-[0-9]+-name')

        url = _urls['yahoo']['owner'] % self.league_num
        soup = BeautifulSoup(self._request(url).text)
        owners = []
        for link in soup.find_all(id=match_owner_link):
            ident = self._owner_id_from_url(link['href'])
            owners.append(Owner(self, ident, link.text.strip()))
        return owners

    def matchups(self, week):
        owner_id = self._owner_id_from_url

        url = _urls['yahoo']['matchup'] % (self.league_num, week)
        rjson = self._request(url).json()
        soup = BeautifulSoup(rjson['content'])
        matchups = []
        for matchup in soup.find('ul').children:
            t1, t2 = list(matchup.find_all('div', class_='Fz-sm'))
            ident1, ident2 = owner_id(t1.a['href']), owner_id(t2.a['href'])
            name1, name2 = t1.text.strip(), t2.text.strip()
            o1, o2 = Owner(self, ident1, name1), Owner(self, ident2, name2)

            matchups.append(Matchup(o1, o2))
        return matchups

    def roster(self, player_search, owner, week):
        def to_pos(row):
            return row.td.find(class_='pos-label')['data-pos'].strip().upper()

        def to_name(row):
            return row.find(class_='ysf-player-name').a.text.strip()

        def to_team(row):
            team_pos = row.find(class_='ysf-player-name').span.text.strip()
            return nfldb.standard_team(re.search('^\S+', team_pos).group(0))

        def pos_group(pos):
            if pos == nfldb.Enums.player_pos.K:
                return self.position_groups['kicking']
            else:
                return self.position_groups['offense']

        def rplayer(r, name, team, pos):
            bench = pos == 'BN'
            if nfldb.standard_team(name) != 'UNK':
                return r.new_player(pos, team, self.position_groups['defense'],
                                    bench, None)
            else:
                player = player_search(name, team=team, position=pos)
                pgroup = pos_group(player.position)
                return r.new_player(pos, team, pgroup, bench, player)

        match_table_id = re.compile('^statTable[0-9]+$')

        url = _urls['yahoo']['roster'] % (self.league_num, owner.ident, week)
        soup = BeautifulSoup(self._request(url).text)

        roster = Roster(self, owner, self.season, week, [])
        for table in soup.find_all(id=match_table_id):
            for row in table.tbody.find_all('tr', recursive=False):
                pos, team, name = to_pos(row), to_team(row), to_name(row)
                roster.players.append(rplayer(roster, name, team, pos))
        return roster

    def _owner_id_from_url(self, url):
        return re.search('%s/([0-9]+)' % self.league_num, url).group(1)

    def _request(self, url):
        r = self._session.get(url)
        soup = BeautifulSoup(r.text)
        if self._login_form(soup):
            self._login()

            r = self._session.get(url)
            soup = BeautifulSoup(r.text)
            if self._login_form(soup):
                raise IOError("Authentication failure.")
        return r

    def _login(self):
        url = 'https://login.yahoo.com/config/login'
        soup = BeautifulSoup(self._session.get(url).text)

        if not self._login_form(soup):
            # Already logged in!
            return

        form = self._login_form(soup)
        params = {'login': self.username, 'passwd': self.password}
        params['.save'] = 'Sign In'
        for inp in form.find_all('input', type='hidden'):
            params[inp['name']] = inp['value']
        r = self._session.post(form['action'], params=params)

        soup = BeautifulSoup(r.text)
        if self._login_form(soup):
            print(soup.prettify().encode('utf-8'))
            err_div = soup.find('div', class_='yregertxt')
            err_msg = 'Unknown error.'
            if err_div:
                err_msg = err_div.text.strip()
            raise IOError('Login failed: %s' % err_msg)

    def _login_form(self, soup):
        return soup.find(id='login_form')


class ESPN (Provider):
    name = 'espn'
    conf_required = []
    conf_optional = []

providers = [ESPN, Yahoo]
