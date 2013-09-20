from __future__ import absolute_import, division, print_function
import codecs
from collections import defaultdict
import copy
import os
import os.path as path
import sys

import toml

import nflfan.provider as provider
import nflfan.score as score

_xdg_home = os.getenv('XDG_CONFIG_HOME')
"""XDG user configuration directory."""

if not _xdg_home:
    home = os.getenv('HOME')
    if not home:
        _xdg_home = ''
    else:
        _xdg_home = path.join(home, '.config')

_data_paths = [
    path.join(_xdg_home, 'nflfan'),
    path.join(sys.prefix, 'share', 'nflfan'),
]
"""A list of paths to check for loading data files."""

_schema = {
    'all': {
        'req': provider.Provider.conf_required,
        'opt': provider.Provider.conf_optional,
    },
}
for prov in provider.providers:
    _schema[prov.name] = {'req': prov.conf_required, 'opt': prov.conf_optional}
"""A down and dirty schema to validate config files."""


def config(file_path=''):
    """
    Reads and loads the configuration file containing fantasy football
    league information.

    The return value is a dictionary mapping provider name (e.g.,
    `yahoo`) to a list of leagues for that provider. Each league
    is guaranteed to have at least a `name`, `season` and `scoring`
    attributes filled in as values that are not `None`. Providers also
    have their own specific mandatory fields:

    `yahoo` must have non-empty values for `consumer_key`,
    `consumer_secret` and `league_id`. In typical cases, the `pin`,
    `request_token` and `request_token_secret` attributes will also be
    set.

    If no configuration file can be found, then an `IOError` is raised.
    """
    def prov_leagues(d):
        return ((k, v) for k, v in d.items() if isinstance(v, dict))

    raw = toml.loads(get_data('config.toml', file_path=file_path))
    scoring = merge(raw['scoring'])
    pos_groups = merge(raw['position_groups'])

    conf = defaultdict(list)
    for prov_name, provider in raw.items():
        if prov_name in ('scoring', 'position_groups'):
            continue

        provider['name'] = prov_name
        for lg_name, lg in prov_leagues(provider):
            apply_schema(scoring, pos_groups, prov_name, provider, lg)
            conf[prov_name].append(lg)
    return conf


def merge(s):
    """
    Given a nesting of TOML dictionaries, return a flat list of each
    scheme in `s`. This applies the inheritance used is configuration
    files so that each scheme has each attribute fully resolved.
    """
    def settings_and_subschemes(d, defaults):
        settings, subs = {}, {}
        for k, v in d.items():
            if isinstance(v, dict):
                subs[k] = v
            else:
                settings[k] = v
        for k, v in defaults.items():
            if k not in settings:
                settings[k] = v
        return copy.deepcopy(settings), subs

    def merge(d, defaults, name):
        settings, subs = settings_and_subschemes(d, defaults)
        schemes[name] = settings
        for subname, subscheme in subs.items():
            fullname = '%s.%s' % (name, subname)
            merge(subscheme, settings, fullname)

    schemes = {}
    for name, scheme in s.items():
        merge(scheme, {}, name)
    return schemes


def get_data(name, file_path=''):
    """
    Reads the contents of a configuration data file with name
    `name`. If `file_path` is given, then it is used if it exists.

    If no file can be found, then an `IOError` is raised.
    """
    if file_path:
        paths = [file_path] + _data_paths
    else:
        paths = _data_paths
    for fp in map(lambda p: path.join(p, name), paths):
        try:
            with codecs.open(fp) as fp:
                return fp.read()
        except IOError:
            pass
    raise IOError("Could not find configuration file %s" % name)


def apply_schema(scoring, pos_groups, prov_name, prov, lg):
    """
    Applies the scheme for the provider `prov_name` to the league `lg`
    while using `prov` as a dictionary of default values for `lg`.
    `scoring` should be a dictionary mapping names to scoring schemes.
    Similarly, `pos_groups` should be a dictionary mapping names to
    position groupings.

    If a required field in the provider's scheme is missing, then a
    `ValueError` is raised.
    """
    def get_scoring(ref):
        try:
            return score.ScoreSchema(ref, scoring[ref])
        except KeyError:
            raise KeyError("Scoring scheme %s does not exist." % ref)

    def get_pos_group(ref):
        try:
            # TOML doesn't have tuples, so convert the two-element lists
            # to a more appropriate representation.
            def to_group(name, fields):
                return provider.PositionGroup(name, map(tuple, fields))

            d = pos_groups[ref]
            return dict([(g, to_group(g, fields)) for g, fields in d.items()])
        except KeyError:
            raise KeyError("Position grouping %s does not exist." % ref)

    def val(key, required=False):
        v = lg.get(key, prov.get(key, None))
        if required and v is None:
            raise ValueError("Provider %s must have %s." % (prov_name, key))
        if key == 'scoring':
            return get_scoring(v)
        elif key == 'position_groups':
            return get_pos_group(v)
        return v

    for r in _schema['all']['req'] + _schema[prov_name]['req']:
        lg[r] = val(r, required=True)
    for o in _schema['all']['opt'] + _schema[prov_name]['opt']:
        lg[o] = val(o)
