import requests
from bs4 import BeautifulSoup
import spotipy
import datetime
from pprint import pprint
from spotipy.oauth2 import SpotifyOAuth
import os

SPOTIFY_SCOPE = "playlist-modify-private"
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URL = "https://example.com"
DATE_FORMAT = '%Y-%m-%d'



# ********************************TODO Step 1 - Scraping the Billboard Hot 100*********************************************
while True:
    date = input(
        'Where year do you want to travel to? Type the date in the format YYYY-MM-DD: ')

    if date.lower() == 'exit':
        break
    else:
        try:
            dateObject = datetime.datetime.strptime(date, DATE_FORMAT)
            print("correct date format")
            break
        except ValueError:
            print("Incorrect data format, should be YYYY-MM-DD")

response = requests.get(
    f'https://www.billboard.com/charts/hot-100/{date}')

# print(response.text)

soup = BeautifulSoup(response.text, 'html.parser')
song_title = soup.find_all('h3', class_="a-truncate-ellipsis")

# print(len(song_title))
song_list = [song_title[song].getText().strip()
             for song in range(len(song_title))]
# print(song_list)

# ***************************************************TODO Step 2 - Authentication with Spotify*******************************
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT_URL, scope=SPOTIFY_SCOPE))

user_id = sp.current_user()['id']
# print(user_id)

# ***************************************************TODO GET TRACK'S URIs*******************************
# https://spotipy.readthedocs.io/en/2.22.1/#spotipy.client.Spotify.search
song_uris = []
year = date.split("-")[0]
for song in song_list:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    # print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"\"{song}\" doesn't exist in Spotify Directory. Skipped.")


# ***************************************************TODO CREATE PLAYLIST*******************************

# https://spotipy.readthedocs.io/en/2.22.1/#spotipy.client.Spotify.user_playlist_create


playlist = sp.user_playlist_create(
    user=user_id, name=f'{date} Billboard Hot 100', public=False)
# pprint(playlist)
PLAYLIST_ID = playlist['id']

# ***************************************************TODO ADD TRACKS TO CREATED PLAYLIST*******************************

# https://spotipy.readthedocs.io/en/2.22.1/#spotipy.client.Spotify.user_playlist_add_tracks
# user_playlist_add_tracks(user, playlist_id, tracks, position=None)

sp.playlist_add_items(playlist_id=PLAYLIST_ID, items=song_uris)
