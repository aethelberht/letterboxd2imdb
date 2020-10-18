#!/usr/bin/env python3
#
# lbd2imdb.py: Takes exported ratings.csv from letterboxd and converts it to
# imdb format so it may then be imported to other services
#
# Does not fill in release date.

from bs4 import BeautifulSoup
import requests
import csv
# from datetime import date
from imdb import IMDb

LETTERBOXD_FILE = 'ratings.csv'
IMDBSTYLE_FILE = 'ratings-imdbfy.csv'

imdb_access = IMDb()

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
    imdb_url = lbxd_soup.find(attrs={"data-track-action": "IMDb"})['href']
    return imdb_access.get_movie(imdb_url.split('/')[4][2:])


def translate_type(kind):
    # Convert kind returned by imdbpy to Title Type
    # FIXME: tvSpecial is unsupported
    types = {
        "movie": "movie",
        "short": "short",
        "video movie": "video",
        "tv movie": "tvMovie",
        "tv mini series": "tvMiniSeries",
        "tv short": "tvShort",
    }
    return types[kind]


def main():
    with open(LETTERBOXD_FILE, newline='') as letterboxd:
        # Expected letterboxd format:
        # Date,Name,Year,Letterboxd URI,Rating
        input_csv = csv.reader(letterboxd, delimiter=',', quotechar='"')
        next(input_csv)
        letterboxd_films = []
        for row in input_csv:
            letterboxd_films.append(row)

    with open(IMDBSTYLE_FILE, 'w', newline='') as outfile:
        head = ["Const", "Your Rating", "Date Rated", "Title", "URL", "Title Type", "IMDb Rating", \
            "Runtime (mins)", "Year", "Genres", "Num Votes", "Release Date", "Directors"]
        filmout = csv.writer(outfile, quoting=csv.QUOTE_MINIMAL)
        filmout.writerow(head)

        for idx, row in enumerate(letterboxd_films):
            if idx > 0 and idx % 20 == 0:
                print(str(idx) + " films processed.")

            title, year = row[1], row[2]
            film = get_imdb_movie(title, year)
            if not film:
                print("Falling back to letterboxd scrape.")
                film = get_movie_via_letterboxd(row[3])
            print(f"found: {film['title']}, {film['year']}")

            # print(f"title: {film['title']}")
            # print(f"imdb rating: {film['rating']} ({film['votes']} votes)")
            # print(f"directors: {', '.join([d['name'] for d in film['directors']])}")
            # print(f"your rating: {int(float(row[4]) * 2)}")
            # print(f"date rated: {row[0]}")
            # print(f"url: http://www.imdb.com/title/tt{film.movieID}/")
            # print(f"genres: {', '.join(film['genres'])}")
            # print(f"type: {film['kind']} -> {translate_type(film['kind'])}")
            if len(film['runtime']) > 1:
                raise ValueError("Multiple runtimes found.")
            else:
                runtime = int(film['runtime'][0])

            if 'directors' in film:
                directors = [d['name'] for d in film['directors']]
            else:
                directors = []

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
                film['votes'],
                '',
                ', '.join([d['name'] for d in film['directors']])
            ])

if __name__ == '__main__':
    main()
