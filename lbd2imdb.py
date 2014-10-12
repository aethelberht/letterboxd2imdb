#! python3
#
# lbd2imdb.py: Takes exported csv from letterboxd and converts it to 
# imdb format so it may then be imported to other services
#
# Does not fill in release date and title type fields as omdbapi does 
# not give complete information on these
#
# 10/11/2014

import json
import requests
import csv
from datetime import date
from bs4 import BeautifulSoup

LETTERBOXD_FILE = 'input.csv'
IMDBSTYLE_FILE = 'output.csv'

with open(LETTERBOXD_FILE, newline='') as csvfile, open(IMDBSTYLE_FILE, 'w', newline='') as outfile:
    filmout = csv.writer(outfile, quoting=csv.QUOTE_ALL)
    filmout.writerow(["position","const","created","modified","description","Title","Title type","Directors","You rated","IMDb Rating","Runtime (mins)","Year","Genres","Num. Votes","Release Date (month/day/year)","URL"])
    filmread = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(filmread)
    idx = 0

    for row in filmread:
        if idx % 20 == 0:
            print(str(idx) + " films processed.")

        # Scrapes letterboxd for imdb link
        r = requests.get(row[3])
        r_soup = BeautifulSoup(r.text)
        s = r_soup.find("p", "text-link").find('a')['href']
        filmid = s.split('/')[4]
        # Grabs json data from imdb-external api
        r = requests.get('http://www.omdbapi.com/?i=' + filmid).json()
        
        rating = str(int(float(row[4]) * 2))
        #if r['Response'] == 'True':
        idx += 1
        rd = row[0].split('-')
        rd = date(int(rd[0]),int(rd[1]),int(rd[2])).strftime('%a %b %d 00:00:00 %Y')
        url = 'http://www.imdb.com/title/' + r['imdbID'] + '/'

        if r['imdbRating'] == 'N/A':
            imdbrating, votes = ('','')
        else:
            imdbrating, votes = (r['imdbRating'], r['imdbVotes'])

        if r['Runtime'] == 'N/A':
            runtime = ''
        else:
            runtime = r['Runtime'][:-4]

        # Extract up to two directors
        director = r['Director'].split(', ')
        director = ', '.join(director[:2])

        genres = r['Genre'].lower()
        genres = genres.replace('sci-fi', 'sci_fi')

        filmout.writerow([str(idx), r['imdbID'], rd, "", "", r['Title'], "", director, rating, imdbrating, runtime, r['Year'], genres, votes, "", url])
            

# Director: Take only two directors

# omdb json format:

# {'imdbID': 'tt0040897',
#  'Response': 'True',
#  'Metascore': 'N/A',
#  'Writer': 'John Huston (screenplay), B. Traven (based on the novel by)',
#  'Genre': 'Action, Adventure, Drama',
#  'Type': 'movie',
#  'Runtime': '126 min',
#  'Country': 'USA',
#  'Rated': 'TV-PG',
#  'Director': 'John Huston',
#  'Released': '24 Jan 1948',
#  'Language': 'English, Spanish',
#  'Title': 'The Treasure of the Sierra Madre',
#  'Poster': 'http://ia.media-imdb.com/images/M/MV5BMTQ4MzUzOTYwOV5BMl5BanBnXkFtZTgwNDA4MzgyMjE@._V1_SX300.jpg',
#  'imdbRating': '8.4',
#  'Year': '1948',
#  'Awards': 'Won 3 Oscars. Another 18 wins & 4 nominations.',
#  'Plot': 'Fred Dobbs and Bob Curtin, two Americans searching for work in Mexico, convince an old prospector to help them mine for gold in the Sierra Madre Mountains.',
#  'imdbVotes': '63,325',
#  'Actors': 'Humphrey Bogart, Walter Huston, Tim Holt, Bruce Bennett'}
