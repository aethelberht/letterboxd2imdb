#!/usr/bin/env python3
#
# lbd2imdb.py: Takes exported ratings.csv from letterboxd and converts it to
# imdb format so it may then be imported to other services
#
# Does not fill in release date.

import argparse
from bs4 import BeautifulSoup
import csv
import os.path
import requests
import time
from imdb import Cinemagoer

imdb_access = Cinemagoer()

def get_imdb_movie(title, year):
    results = [r for r in imdb_access.search_movie(title) if r['title'] == title and 'year' in r and \
        r['year'] == int(year) and r['kind'] not in ['video game', 'episode']]
    if len(results) == 1:
        imdb_access.update(results[0], info=['main'])
        return results[0]
    elif len(results) == 0:
        print(f"No results found for {title} ({year})")
    elif len(results) > 1:
        print(f"Multiple results found for {title} ({year})")
    return None


def get_movie_via_letterboxd(url):
    # Scrapes letterboxd for imdb link
    lbxd_data = requests.get(url)
    lbxd_soup = BeautifulSoup(lbxd_data.text, features="lxml")
    try:
        imdb_url = lbxd_soup.find(attrs={"data-track-action": "IMDb"})['href']
    except TypeError:
        return None
    return imdb_access.get_movie(imdb_url.split('/')[4][2:])


def translate_type(kind):
    # Convert kind returned by imdbpy to Title Type
    # FIXME: tvSpecial is unsupported (assigned to movie instead)
    types = {
        "movie": "movie",
        "short": "short",
        "video movie": "video",
        "tv movie": "tvMovie",
        "tv mini series": "tvMiniSeries",
        "tv short": "tvShort",
        "episode": "tvEpisode"
    }
    return types[kind]


def main(letterboxd_file, imdbstyle_file):
    with open(letterboxd_file, newline='', encoding='utf-8') as letterboxd:
        # Expected letterboxd format:
        # Date,Name,Year,Letterboxd URI,Rating
        input_csv = csv.reader(letterboxd, delimiter=',', quotechar='"')
        next(input_csv)
        letterboxd_films = []
        for row in input_csv:
            letterboxd_films.append(row)

    skipped = []

    with open(imdbstyle_file, 'w', newline='') as outfile:
        head = ["Const", "Your Rating", "Date Rated", "Title", "URL", "Title Type", "IMDb Rating", \
            "Runtime (mins)", "Year", "Genres", "Num Votes", "Release Date", "Directors"]
        filmout = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
        filmout.writerow(head)

        for idx, row in enumerate(letterboxd_films):
            start = time.time()
            if idx > 0 and idx % 20 == 0:
                print(str(idx) + " films processed.")

            title, year = row[1], row[2]
            film = get_imdb_movie(title, year)
            if not film:
                print("Falling back to letterboxd scrape.")
                if row[3] == '':
                    print(f"Warning: exported csv is missing letterboxd url for {title}, {year}. Skipping.")
                    skipped.append(row[:] + ['missingLetterboxdUrl'])
                    continue
                film = get_movie_via_letterboxd(row[3])
                if not film:
                    print(f"Warning: Letterboxd page doesn't have a link to an IMDb entry. Skipping.")
                    skipped.append(row[:] + ['missingImdbUrl'])
                    continue

            # print(f"title: {film['title']}")
            # print(f"imdb rating: {film['rating']} ({film['votes']} votes)")
            # print(f"directors: {', '.join([d['name'] for d in film['directors']])}")
            # print(f"your rating: {int(float(row[4]) * 2)}")
            # print(f"date rated: {row[0]}")
            # print(f"url: http://www.imdb.com/title/tt{film.movieID}/")
            # print(f"genres: {', '.join(film['genres'])}")
            # print(f"type: {film['kind']} -> {translate_type(film['kind'])}")
            if 'runtimes' not in film:
                print(f"Warning: Runtime not found for {film['title']} id {film.movieID}. Leaving blank.")
                runtime = ''
            elif len(film['runtimes']) > 1:
                print(f"Warning: Multiple runtimes found for {film['title']} id {film.movieID}. Skipping.")
                skipped.append(row[:] + ['multipleRuntimes'])
            else:
                runtime = int(film['runtimes'][0])

            if 'directors' in film:
                directors = [d['name'] for d in film['directors']]
            else:
                directors = []

            if 'votes' in film:
                votes = film['votes']
            else:
                votes = 0


            filmout.writerow([
                f"tt{film.movieID}",
                int(float(row[4]) * 2),
                row[0],
                film['title'],
                f"http://www.imdb.com/title/tt{film.movieID}/",
                translate_type(film['kind']),
                runtime,
                film['year'],
                ', '.join(film['genres']),
                votes,
                '',
                ', '.join(directors)
            ])

            end = time.time()
            print(f"processed: {film['title']}, {film['year']} in {end - start:.2f} seconds")

        print("\nProcessing finished. Here are the entries which were not converted due to errors:")
        for row in skipped:
            print(row)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="ratings file exported from letterboxd, ratings.csv by default",
        metavar="FILE", default="ratings.csv")
    parser.add_argument("-o", help="output file, output.csv by default",
        metavar="FILE", default="output.csv")
    args = parser.parse_args()
    if not os.path.exists(args.i):
        print(f"ERROR: {args.i} doesn't exist.")
        quit()
    else:
        main(args.i, args.o)
