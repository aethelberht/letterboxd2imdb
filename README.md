Letterboxd to IMDB Converter
=========

## Overview

This Python 3 script takes a user's rating file exported from [Letterboxd](http://letterboxd.com/) and converts it to that of IMDB's csv format. The output can then be other sites which support importing from IMDB but not Letterboxd, such as [Criticker](http://criticker.com/) and [I Check Movies](http://www.icheckmovies.com/).

## Known Issues

* The unofficial API being used to lookup corresponding IMDB data fails to make fine-grained distinctions for the "Title type" field, so it is left blank. Importers, unsurprisingly, don't seem to care about the contents of this field.
