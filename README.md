Letterboxd Export to IMDb Converter
=========

## Overview

This Python 3 script takes a user's rating file (`ratings.csv`) exported from [Letterboxd](http://letterboxd.com/) and converts it to that of IMDb's csv format. The output can then be imported to other sites which support importing from IMDB but not Letterboxd, such as [Criticker](http://criticker.com/) and [ICheckMovies](http://www.icheckmovies.com/). The script accesses IMDb for each entry (and also accesses Letterboxd if an initial IMDb search fails), so expect it to take at least 2-3 seconds per movie.

Requirements: `bs4` (Beautiful Soup), `requests`, and [IMDbPy](https://imdbpy.github.io/).

Usage:
```
python3 lbd2imdb.py [-h] [-i FILE] [-o FILE]

optional arguments:
  -h, --help  show this help message and exit
  -i FILE     ratings file exported from letterboxd, ratings.csv by default
  -o FILE     output file, output.csv by default
```

## Known Issues

* The `Release Date` field is left blank in the exported csv file. The `Year` field is supported.
* TV Specials are labeled as `movie` instead of `tvSpecial` in the exported file.
