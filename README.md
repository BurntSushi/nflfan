NFLfan is a web application that provides a user interface for searching NFL 
data (back to 2009), collecting all of your fantasy teams into one place for
live scoring updates and **watching video of any play** available on your 
system.

These features are a *culmination* of the following projects:

* [nflgame](https://github.com/BurntSushi/nflgame) - Retrieve statistics from 
  NFL's JSON feed. This reverse engineers the JSON feed into easily searchable 
  statistics and caches JSON game data to disk.
* [nfldb](https://github.com/BurntSushi/nfldb) - Stores statistics from 
  `nflgame` in a relational PostgreSQL database. This provides a convenient and 
  programmatic querying interface and also meets the performance requirements 
  for a simple web application.
* [nflvid](https://github.com/BurntSushi/nflvid) - A rough-around-the-edges 
  command line tool to download broadcast footage from publicly available 
  sources **and slice that footage into play-by-play segments**.

This README is pretty sparse at the moment. It will be fleshed out a bit more 
before the season starts.


## Demo

Coming soon. (This will be a video since I cannot provide a public web service 
that distributed NFL broadcast footage.)

I will also provide a *real* demo that lacks NFL broadcast footage.


## Installation

`nflfan` can be installed with `pip`:

```
pip install nflfan
```

Note that `nflfan` requires a running instance of `nfldb`. Since this means 
setting up and importing a PostgreSQL database, we have some [installation 
instructions here](https://github.com/BurntSushi/nfldb/wiki/Installation).

Once `nflfan` is installed, you'll want to configure it. Here is a [sample 
config 
file](https://github.com/BurntSushi/nflfan/blob/master/config.sample.toml) with 
documentation. (Configuration will need to be fleshed out more.)


## Loading fantasy teams

After `nflfan` is installed, a script called `nflfan-update` will be available. 
This should update you fantasy rosters as configured in `config.toml`.

This script looks pretty broken right now. I will fix it shortly before the 
regular season starts.


## Technology stack

Including all of the other `nfl*` projects, the following tech is used:

* Python as the main backend programming language.
* PostgreSQL for the database.
* RequireJS, jQuery, Bootstrap and Knockout for the frontend.
* Bottle for the web framework. (Web server is customizable, but I prefer
  [bjoern](https://github.com/jonashaag/bjoern) for deployment. For local 
  single user mode, the default `wsgiref` development server is quite 
  suitable.)
* Something resembling a REST interface is exposed in the `nflfan.web` module, 
  but it needs some love and documentation. (I am skeptical that a full REST 
  interface is warranted.)

I'm not much of a frontend guy, so the Javascript is a bit of a mess and 
undocumented. However, considering the power of the UI, I think there is 
surprisingly little of it. (Kudos to Knockout for that one, I think.)

