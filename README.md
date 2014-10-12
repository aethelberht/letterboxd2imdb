Letterboxd to IMDB Converter
=========

## Overview

This Python 3 script takes a user's rating file exported from [Letterboxd](http://letterboxd.com/) and converts it to that of IMDB's csv format. The output can then be imported to other sites which support importing from IMDB but not Letterboxd such as [Criticker](http://criticker.com/) and [ICheckMovies](http://www.icheckmovies.com/).

Requires `bs4` (Beautiful Soup) and `requests`.

Configure `LETTERBOXD_FILE` and `OUTPUT` variables as desired and run the script.

The script uses [OMDbAPI](http://omdbapi.com/) for IMDB data lookup.

## Known Issues

* While OMDbAPI has a title search feature of its own, it was stumbling on things like [20 Feet from Stardom](http://www.imdb.com/title/tt2396566/combined) being matched with a [movie review show](http://www.imdb.com/title/tt3127024/combined) that was reviewing that movie. To maintain accuracy, the script currently first queries Letterboxd to retrieve the exact imdb ID -- which is, unfortunately, *slow*. This will be looked into.
* OMDbAPI fails to make fine-grained distinctions for the "Title type" and "Release date" fields so they are left blank. Importers, unsurprisingly, don't seem to care about their contents.
* There's a handful of titles where the runtime isn't properly grabbed for some reason.
