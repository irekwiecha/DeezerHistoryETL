import os
import pandas as pd
import requests
import time
import sqlite3
from datetime import datetime as dt
from datetime import timedelta as td
from dotenv import load_dotenv
from private import user_id, app_id, app_secret_key

USER_ID = user_id           # hard code your own id or create in private/__init__.py
APP_ID = app_id             # hard code your own id or create in private/__init__.py
APP_KEY = app_secret_key    # hard code your own key or create in private/__init__.py
DAYS_TO_FILTER = 1          # If you want to run the script at the end of the day set to 0

'''
Before you can use this tool, you first need to declare your Deezer app in their developer portal:
https://developers.deezer.com/myapps/create 
Create a new app with the following Redirect URL: http://localhost:8080/oauth/return
this is necessary for the `deezer-oauth-cli` packages to work.
'''


def get_token():
    # automatic process of create an API Token from deezer
    print('Authorize the token in the browser')
    print('\nA browser window will open for authorization...')
    time.sleep(3)
    os.system(f'deezer-oauth {APP_ID} {APP_KEY}')
    print('Authorization token retrieved\n')


def get_history(user_id, API_TOKEN):
    # gets data from the generated address
    urls = [f'http://api.deezer.com/user/{user_id}/history?access_token={API_TOKEN}&index={index}' for index in [0, 50]]
    resp_data = []
    for url in urls:
        try:
            r = requests.get(url)
            resp_data.append(r.json())
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
    return resp_data


def fill_dict(song_dict, resp_data):
    # prepare data (fill the dict) to create a DataFrame
    dif = ((dt.now() - dt.utcnow())) / td(hours=1)  # time difference in relation to UTC,
    for data in resp_data:
        for song in data['data']:
            song_dict['song_name'].append(song['title'])
            song_dict['artist_name'].append(song['artist']['name'])
            song_dict['played_at'].append((dt.utcfromtimestamp(song['timestamp']) + td(hours=dif)).strftime("%d.%m.%y %H:%M:%S"))
            song_dict['timestamp'].append(dt.utcfromtimestamp(song['timestamp']).strftime("%d.%m.%y"))


def validation_data(df):
    # check if DataFrame is empty
    if df.empty:
        print('No tracks downloaded. Finishing execution')
        return False
    # primary key check
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception('Primary Key Check Failed')
    # check for nulls
    if df.isnull().values.any():
        raise Exception('Null valued found')
    return True


# Extract

# initializes dictionary that store data
song_dict = {
    "song_name": [],
    "artist_name": [],
    "played_at": [],
    "timestamp": []
}

# call api_token & creat history data
api_token = os.getenv('API_TOKEN')
history = get_history(user_id, api_token)

# checks if the api token is valid, if not, it calls the get_token function
try:
    fill_dict(song_dict, history)
except KeyError:
    get_token()
    load_dotenv(override=True)
    api_token = os.getenv('API_TOKEN')
    history = get_history(user_id, api_token)
    fill_dict(song_dict, history)

# date declaration to the "filter"
date_to_filter = (dt.now() - td(days=DAYS_TO_FILTER)).strftime("%d.%m.%y")

# creat a "filter" DataFrame
song_df = pd.DataFrame(song_dict, columns=["song_name", "artist_name", "played_at", "timestamp"])
filter_song_df = song_df["timestamp"] == date_to_filter
song_df = song_df.where(filter_song_df).dropna()

# Validate

if validation_data(song_df):
    print('Data valid, proceed to Load stages')

# Load

conn = sqlite3.connect('my_tracks.sqlite')
cursor = conn.cursor()

sql_query = """
CREATE TABLE IF NOT EXISTS my_tracks(
    song_name VARCHAR(200),
    artist_name VARCHAR(200),
    played_at VARCHAR(200),
    timestamp VARCHAR(200),
    CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
)
"""

cursor.execute(sql_query)
print('Open database...')

try:
    song_df.to_sql('my_tracks', conn, index=False, if_exists='append')
    print('>>> updating data <<<')
except:
    print('Data already exists in the database')

conn.close()
print('...Close database\n')

# input('Press "ENTER" key to exit')
