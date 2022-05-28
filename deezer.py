import os
import pandas as pd
import requests
import time
from datetime import datetime as dt
from datetime import timedelta as td
from dotenv import load_dotenv
from private import user_id, app_id, app_secret_key

USER_ID = user_id           # hard code your own id or creat in private/__init__.py
APP_ID = app_id             # hard code your own id or creat in private/__init__.py
APP_KEY = app_secret_key    # hard code your own key or creat in private/__init__.py


def get_token():
    print('Authorize the token in the browser')
    print('\nA browser window will open for authorization...')
    time.sleep(3)
    os.system(f'deezer-oauth {APP_ID} {APP_KEY}')
    print('Authorization token retrieved\n')


def get_history(user_id, API_TOKEN):
    url = f'http://api.deezer.com/user/{user_id}/history?access_token={API_TOKEN}'
    try:
        r = requests.get(url)
        history = r.json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    return history


def fill_dict(song_dict, history):
    for song in history['data']:
        song_dict['song_name'].append(song['title'])
        song_dict['artist_name'].append(song['artist']['name'])
        song_dict['played_at'].append((dt.utcfromtimestamp(song['timestamp']) + td(hours=dif)).strftime("%d.%m.%y %H:%M:%S"))
        song_dict['timestamp'].append(dt.utcfromtimestamp(song['timestamp']).strftime("%d.%m.%y"))


dif = ((dt.now() - dt.utcnow())) / td(hours=1)
yesterday = (dt.now() - td(days=1)).strftime("%d.%m.%y")

song_dict = {
    "song_name": [],
    "artist_name": [],
    "played_at": [],
    "timestamp": []
}

api_token = os.getenv('API_TOKEN')
history = get_history(USER_ID, api_token)

if 'error' in history:
    get_token()
    load_dotenv(override=True)
    api_token = os.getenv('API_TOKEN')
    history = get_history(user_id, api_token)
    fill_dict(song_dict, history)
else:
    fill_dict(song_dict, history)


song_df = pd.DataFrame(song_dict, columns=["song_name", "artist_name", "played_at", "timestamp"])
filter_yeasterday = song_df["timestamp"] == yesterday
to_db = song_df.where(filter_yeasterday).dropna()
print(to_db.head())

print('Database updated successfully')
input('Press ENTER key to exit')
