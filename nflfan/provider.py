from __future__ import absolute_import, division, print_function

from collections import namedtuple
import json
import multiprocessing.pool
import os
import re
import sys

import requests

from bs4 import BeautifulSoup

import nfldb

import nflfan.config

__pdoc__ = {}

_user_agent = 'Mozilla/5.0 (X11; Linux x86_64)'
"""
The user agent string is heuristically determined. Namely, I was having
problems getting some providers to authenticate with more vague user
agent strings.

You may want to use a different user agent string entirely if you're
writing your own provider.
"""

_urls = {
    'yahoo': {
        'owner': 'http://football.fantasysports.yahoo.com/f1/%s/teams',
        'matchup': 'http://football.fantasysports.yahoo.com/f1/%s/'
                   'matchup?matchup_week=%d&ajaxrequest=1',
        'roster': 'http://football.fantasysports.yahoo.com/f1/%s/%s?week=%d',
    },
    'espn': {
        'owner': 'http://games.espn.go.com/ffl/leaguesetup'
                 '/ownerinfo?leagueId={league_id}&seasonId={season_id}',
        'matchup': 'http://games.espn.go.com/ffl/scoreboard?'
                   'leagueId={league_id}&matchupPeriodId={week}'
                   '&seasonId={season_id}',
        'roster': 'http://games.espn.go.com/ffl/playertable/prebuilt/'
                  'manageroster?leagueId={league_id}&teamId={team_id}'
                  '&seasonId={season_id}&scoringPeriodId={week}'
                  '&view=overview&context=clubhouse'
                  '&ajaxPath=playertable/prebuilt/manageroster'
                  '&managingIr=false&droppingPlayers=false&asLM=false',
    },
}


def pp(soup):
    print(soup.prettify().encode('utf-8'))


def eprint(*args, **kwargs):
    kwargs['file'] = sys.stderr
    args = ['[nflfan]'] + list(args)
    print(*args, **kwargs)


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


class League (namedtuple('League',
                         'season phase ident prov_name name scoring conf')):
    __pdoc__['League.season'] = \
        """The year of the NFL season for this league."""

    __pdoc__['League.phase'] = \
        """The phase of the season: preseason, regular or post."""

    __pdoc__['League.ident'] = \
        """
        A unique identifier for this league. The type and format of
        this value is provider dependent.
        """

    __pdoc__['League.prov_name'] = \
        """The name of the provider for this league."""

    __pdoc__['League.name'] = \
        """The name of this league from the configuration."""

    __pdoc__['League.scoring'] = \
        """The `nflfan.ScoreSchema` for this league."""

    __pdoc__['League.conf'] = \
        """
        A dictionary of configuration settings. The keys and values in
        this dictionary are provider dependent.
        """

    def __init__(self, *args):
        super(League, self).__init__(*args)
        self._cache = {}

    @property
    def full_name(self):
        return '%s.%s' % (self.prov_name, self.name)

    def is_me(self, obj):
        if not self.conf.get('me', None):
            return False

        if isinstance(obj, Roster):
            return self.is_me(obj.owner)
        elif isinstance(obj, Matchup):
            return self.is_me(obj.owner1) or self.is_me(obj.owner2)
        else:
            return self.conf['me'].lower() in obj.name.lower()

    def me(self, objs):
        for obj in objs:
            if self.is_me(obj):
                return obj
        return None

    def owners(self, week):
        return self._cached(week, 'owners')

    def owner(self, week, ident):
        for o in self.owners(week):
            if o.ident == ident:
                return o
        return None

    def matchups(self, week):
        return self._cached(week, 'matchups')

    def matchup(self, week, ident):
        for m in self.matchups(week):
            if m.owner1.ident == ident or m.owner2.ident == ident:
                return m
        return None

    def rosters(self, week):
        return self._cached(week, 'rosters')

    def roster(self, week, ident):
        for r in self.rosters(week):
            if r.owner.ident == ident:
                return r
        return None

    def cache_path(self, week):
        return os.path.join(nflfan.config.cache_path(),
                            str(self.season), str(self.phase), str(week),
                            self.full_name + '.json')

    def _cached(self, week, key):
        if week not in self._cache:
            self._load(week)
        return self._cache[week][key]

    def _load(self, week):
        raw = None
        fp = self.cache_path(week)
        try:
            with open(fp) as f:
                raw = json.load(f)
        except IOError:
            raise IOError(
                "No cached data for week %d in %s could be found at %s\n"
                "Have you run `nflfan-update --week %d` yet?"
                % (week, self.full_name, fp, week))

        d = {'owners': [], 'matchups': [], 'rosters': []}
        for owner in raw['owners']:
            d['owners'].append(Owner._make(owner))
        for matchup in raw['matchups']:
            o1 = None if matchup[0] is None else Owner._make(matchup[0])
            o2 = None if matchup[1] is None else Owner._make(matchup[1])
            d['matchups'].append(Matchup(o1, o2))
        for roster in raw['rosters']:
            o = Owner._make(roster[0])
            r = Roster(o, roster[1], roster[2], [])
            for rp in roster[3]:
                r.players.append(RosterPlayer._make(rp))
            d['rosters'].append(r)
        self._cache[week] = d

    def __str__(self):
        return self.full_name


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

    def other(self, ident):
        """
        Given an identifier for one of the owner's in this matchup,
        return the `nflfan.Owner` of the other owner.
        """
        assert ident in (self.owner1.ident, self.owner2.ident)
        if ident == self.owner1.ident:
            return self.owner2
        else:
            return self.owner1

    def __str__(self):
        return '%s vs. %s' % (self.owner1, self.owner2)


class Owner (namedtuple('Owner', 'ident name')):
    __pdoc__['Owner.ident'] = \
        """
        A unique identifier corresponding to this owner. The type
        of this value is provider-dependent.
        """

    __pdoc__['Owner.name'] = \
        """A string representing the name of this owner."""

    def __str__(self):
        return self.name


class Roster (namedtuple('Roster', 'owner season week players')):
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

    def new_player(self, pos, team, bench, player_id):
        """
        A convenience method for creating a new `nflfan.RosterPlayer`
        given the current roster.
        """
        return RosterPlayer(pos, team, bench, self.season, self.week,
                            None, 0.0, None, player_id)

    @property
    def active(self):
        return filter(lambda rp: not rp.bench, self.players)

    @property
    def benched(self):
        return filter(lambda rp: rp.bench, self.players)

    @property
    def points(self):
        """Returns the total number of points for non-benched players."""
        return sum(p.points for p in self.players if not p.bench)

    def __str__(self):
        s = []
        for rp in self.players:
            s.append(str(rp))
        return '\n'.join(s)


class RosterPlayer (
    namedtuple('RosterPlayer',
               'position team bench season week '
               'game points player player_id')):
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

    __pdoc__['RosterPlayer.bench'] = \
        """A boolean indicating whether this is a bench position or not."""

    __pdoc__['RosterPlayer.season'] = \
        """The year of the corresponding NFL season."""

    __pdoc__['RosterPlayer.week'] = \
        """The week number in which this roster was set."""

    __pdoc__['RosterPlayer.game'] = \
        """
        The `nfldb.Game` object for the game that this player played
        in. If this roster position corresponds to a bye week, then
        this attribute is set to `None`.
        """

    __pdoc__['RosterPlayer.points'] = \
        """The total fantasy points for this roster player."""

    __pdoc__['RosterPlayer.player'] = \
        """
        A `nfldb.Player` object corresponding to this roster player.

        This attribute is `None` by default, and is always `None` for
        roster players corresponding to entire teams (e.g., defense).
        """

    __pdoc__['RosterPlayer.player_id'] = \
        """
        A player id string corresponding to the player in this roster
        position and a player in nfldb. This may be `None` when the
        roster player corresponds to an entire team. (e.g., A defense.)
        """

    @property
    def is_empty(self):
        return self.team is None and self.player_id is None

    @property
    def is_defense(self):
        return self.team is not None and self.player_id is None

    @property
    def is_player(self):
        return self.player_id is not None

    @property
    def id(self):
        if self.is_empty:
            return 'Empty'
        elif self.is_defense:
            return self.team
        else:
            return self.player_id

    @property
    def name(self):
        return self.id if not self.player else self.player.full_name

    def __str__(self):
        if self.game is not None and self.game.is_playing:
            playing = '*'
        else:
            playing = ' '
        return '%-6s %-4s %-20s %s%0.2f' \
               % (self.position, self.team, self.name, playing, self.points)


class Provider (object):
    """
    This class describes the interface that each fantasy football
    provider must implement so that it can work with nflfan. In other
    words, this is an abstract base class that should **not** be
    instantiated directly.

    All public members of this class must also be defined in each
    provider implementation, including the class variables.
    """

    provider_name = None
    """The name of the provider used in the configuration file."""

    conf_required = ['scoring', 'league_name', 'season', 'phase', 'league_id']
    """A list of fields required for every provider."""

    conf_optional = ['me']
    """A list of fields that are optional for every provider."""

    def __init__(self, lg):
        self._lg = lg
        self._session = requests.Session()
        self._session.headers.update(getattr(self, '_headers', {}))

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
        `nflfan.Roster` object. The `nflfan.Roster` contains a list of
        `nfldb.Player` objects and their corresponding position on the
        roster.

        `player_search` should be a function that takes a full
        player name and returns the closest matching player as a
        `nfldb.Player` object. It should also optionally take keyword
        arguments `team` and `position` that allow for extra filtering.

        Note that the roster position is a string but the set of
        possible values is provider dependent. It is used for display
        purposes only.
        """
        assert False, 'subclass responsibility'

    def save(self, fp, player_search, week):
        """
        Writes a JSON encoding of all the owners, matchups and rosters
        for the given week to a file at `fp`.

        `player_search` should be a function that takes a full
        player name and returns the closest matching player as a
        `nfldb.Player` object. It should also optionally take keyword
        arguments `team` and `position` that allow for extra filtering.
        """
        d = {
            'owners': self.owners(),
            'matchups': self.matchups(week),
        }

        # I'm hoping this doesn't hurt custom providers that don't need
        # to do IO to fetch a roster.
        def roster(owner):
            return self.roster(player_search, owner, week)

        # pool = multiprocessing.pool.ThreadPool(3) 
        # d['rosters'] = pool.map(roster, d['owners']) 
        d['rosters'] = map(roster, d['owners'])
        json.dump(d, open(fp, 'w+'))

    def _request(self, url):
        eprint('download %s' % url)
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
        assert self._login_url is not None
        soup = BeautifulSoup(self._session.get(self._login_url).text)

        if not self._login_form(soup):
            # Already logged in!
            return

        form = self._login_form(soup)
        params = self._login_params()
        for inp in form.find_all('input', type='hidden'):
            params[inp['name']] = inp['value']
        r = self._session.post(form['action'], params=params)
        return BeautifulSoup(r.text)

    def _login_params(self):
        assert False, 'subclass responsibility'

    def _login_form(self, soup):
        assert False, 'subclass responsibility'

    def __str__(self):
        return self.__class__.provider_name


class Yahoo (Provider):
    provider_name = 'yahoo'
    conf_required = []
    conf_optional = ['username', 'password']
    _headers = {'User-Agent': _user_agent}
    _login_url = 'https://login.yahoo.com/config/login'

    def __init__(self, lg):
        super(Yahoo, self).__init__(lg)
        _, _, self._league_num = self._lg.ident.split('.')

    def owners(self):
        match_owner_link = re.compile('team-[0-9]+-name')

        url = _urls['yahoo']['owner'] % self._league_num
        soup = BeautifulSoup(self._request(url).text)
        owners = []
        for link in soup.find_all(id=match_owner_link):
            ident = self._owner_id_from_url(link['href'])
            owners.append(Owner(ident, link.text.strip()))
        return owners

    def matchups(self, week):
        mk_owner = lambda div: Owner(owner_id(div.a['href']), div.text.strip())
        owner_id = self._owner_id_from_url

        url = _urls['yahoo']['matchup'] % (self._league_num, week)
        rjson = self._request(url).json()
        soup = BeautifulSoup(rjson['content'])
        matchups = []
        for matchup in soup.find('ul').children:
            pair = list(matchup.find_all('div', class_='Fz-sm'))
            if len(pair) == 1:
                matchups.append(Matchup(mk_owner(pair[0]), None))
            else:
                matchups.append(Matchup(mk_owner(pair[0]), mk_owner(pair[1])))
        return matchups

    def roster(self, player_search, owner, week):
        def to_pos(row):
            return row.td.find(class_='pos-label')['data-pos'].strip().upper()

        def to_name(row):
            return row.find(class_='ysf-player-name').a.text.strip()

        def to_team(row):
            team_pos = row.find(class_='ysf-player-name').span.text.strip()
            return nfldb.standard_team(re.search('^\S+', team_pos).group(0))

        def rplayer(r, name, team, pos):
            bench = pos == 'BN'
            if name is None and team is None:
                return r.new_player(pos, None, bench, None)
            elif nfldb.standard_team(name) != 'UNK':
                return r.new_player(pos, team, bench, None)
            else:
                player = player_search(name, team=team, position=pos)
                return r.new_player(pos, team, bench, player.player_id)

        match_table_id = re.compile('^statTable[0-9]+$')

        url = _urls['yahoo']['roster'] % (self._league_num, owner.ident, week)
        soup = BeautifulSoup(self._request(url).text)

        roster = Roster(owner, self._lg.season, week, [])
        for table in soup.find_all(id=match_table_id):
            for row in table.tbody.find_all('tr', recursive=False):
                pos = to_pos(row)
                try:
                    team, name = to_team(row), to_name(row)
                    roster.players.append(rplayer(roster, name, team, pos))
                except AttributeError:
                    roster.players.append(rplayer(roster, None, None, pos))
        return roster

    def _owner_id_from_url(self, url):
        return re.search('%s/([0-9]+)' % self._league_num, url).group(1)

    def _login(self):
        soup = super(Yahoo, self)._login()
        if self._login_form(soup):
            err_div = soup.find('div', class_='yregertxt')
            err_msg = 'Unknown error.'
            if err_div:
                err_msg = err_div.text.strip()
            raise IOError('Login failed: %s' % err_msg)

    def _login_params(self):
        return {
            'login': self._lg.conf.get('username', ''),
            'passwd': self._lg.conf.get('password', ''),
            '.save': 'Sign In',
        }

    def _login_form(self, soup):
        return soup.find(id='login_form')


class ESPN (Provider):
    provider_name = 'espn'
    conf_required = []
    conf_optional = ['username', 'password']
    _headers = {'User-Agent': _user_agent}
    _login_url = 'http://games.espn.go.com/ffl/signin?_=_'

    def owners(self):
        url = _urls['espn']['owner'].format(
            league_id=self._lg.ident, season_id=self._lg.season)
        soup = BeautifulSoup(self._request(url).text)
        owners = []
        for td in soup.select('tr.ownerRow td.teamName'):
            ident = self._owner_id_from_url(td.a['href'])
            owners.append(Owner(ident, td.text.strip()))
        return owners

    def matchups(self, week):
        owner_id = self._owner_id_from_url

        url = _urls['espn']['matchup'].format(
            league_id=self._lg.ident, season_id=self._lg.season, week=week)
        soup = BeautifulSoup(self._request(url).text)
        matchupDiv = soup.find(id='scoreboardMatchups')
        matchups = []
        for table in matchupDiv.select('table.matchup'):
            t1, t2 = list(table.find_all(class_='name'))
            id1, id2 = owner_id(t1.a['href']), owner_id(t2.a['href'])
            name1, name2 = t1.a.text.strip(), t2.a.text.strip()
            o1, o2 = Owner(id1, name1), Owner(id2, name2)

            matchups.append(Matchup(o1, o2))
        return matchups

    def roster(self, player_search, owner, week):
        def to_pos(row):
            pos = row.find(class_='playerSlot').text.strip().upper()
            if pos == 'BENCH':
                return 'BN'
            return pos

        def to_name(row):
            name = row.find(class_='playertablePlayerName').a.text.strip()

            # If this is the defense, apparently 'D/ST' is included in
            # the name. Wtf?
            return re.sub('\s+D/ST$', '', name)

        def to_team(row):
            tpos = row.find(class_='playertablePlayerName').a.next_sibling
            tpos = tpos.strip(' \r\n\t*,|').upper()

            # This is a little weird because the team name seems to run
            # in with the position. Perhaps a weird encoding quirk?
            if len(tpos) < 2:
                return 'UNK'
            elif len(tpos) == 2:
                return nfldb.standard_team(tpos)
            else:
                team = nfldb.standard_team(tpos[0:3])
                if team == 'UNK':
                    team = nfldb.standard_team(tpos[0:2])
                return team

        def rplayer(r, name, team, pos):
            bench = pos == 'BN'
            name_team = nfldb.standard_team(name)
            if name is None and team is None:
                return r.new_player(pos, None, bench, None)
            elif name_team != 'UNK':
                return r.new_player(pos, name_team, bench, None)
            else:
                player = player_search(name, team=team, position=pos)
                return r.new_player(pos, team, bench, player.player_id)

        url = _urls['espn']['roster'].format(
            league_id=self._lg.ident, season_id=self._lg.season, week=week,
            team_id=owner.ident)
        soup = BeautifulSoup(self._request(url).text)

        roster = Roster(owner, self._lg.season, week, [])
        for tr in soup.select('tr.pncPlayerRow'):
            if tr.get('id', '') == 'pncEmptyRow':
                continue
            pos = to_pos(tr)
            try:
                team, name = to_team(tr), to_name(tr)
                roster.players.append(rplayer(roster, name, team, pos))
            except AttributeError:
                roster.players.append(rplayer(roster, None, None, pos))
        return roster

    def _owner_id_from_url(self, url):
        return re.search('teamId=([0-9]+)', url).group(1)

    def _login(self):
        soup = super(ESPN, self)._login()
        if self._login_form(soup):
            err_msg = []
            for msg in soup.find_all('font', color='#ff0000'):
                err_msg.append(msg.text.strip())
            err_msg = '\n'.join(err_msg) if err_msg else 'Unknown error.'
            raise IOError('Login failed: %s' % err_msg)

    def _login_params(self):
        return {
            'username': self._lg.conf.get('username', ''),
            'password': self._lg.conf.get('password', ''),
            'submit': 'Sign In',
        }

    def _login_form(self, soup):
        return soup.find('form', attrs={'name': 'loginForm'})
