import os
import sqlite3
import time
from datetime import datetime as dt
from datetime import timedelta as td

import pandas as pd
import requests
from dotenv import load_dotenv

from private import app_id, app_secret_key, user_id

USER_ID = user_id  # hard code your own id or create in private/__init__.py
APP_ID = app_id  # hard code your own id or create in private/__init__.py
APP_KEY = app_secret_key  # hard code your own key or create in private/__init__.py
DAYS_TO_FILTER = 1  # If you want to run the script at the end of the day set to 0

# date declaration for "filter"
date_to_filter = (dt.now() - td(days=DAYS_TO_FILTER)).date()

"""
Before you can use this tool, you first need to declare your Deezer app in their developer portal:
https://developers.deezer.com/myapps/create 
Create a new app with the following Redirect URL: http://localhost:8080/oauth/return
this is necessary for the `deezer-oauth-cli` package to work.
"""


def get_token():
    # automatic process of create an API Token from deezer
    print("Authorize the token in the browser")
    print("\nA browser window will open for authorization...")
    time.sleep(1.5)
    os.system(f"deezer-oauth {APP_ID} {APP_KEY}")
    print("Authorization token retrieved\n")


def get_history(user_id, API_TOKEN):
    # retrieving data from from generated urls
    urls = [
        f"http://api.deezer.com/user/{user_id}/history?access_token={API_TOKEN}&index={index}"
        for index in [0, 50]
    ]
    resp_data = []
    for url in urls:
        try:
            r = requests.get(url)
            r.raise_for_status()
            resp_data.append(r.json())
        except requests.exceptions.HTTPError as e:
            raise SystemExit(e)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
    return resp_data


def fill_dict(song_dict, resp_data):
    # prepare the data (filling the dict) to create a DataFrame
    dif = ((dt.now() - dt.utcnow())) / td(hours=1)  # time difference to UTC
    for data in resp_data:
        for song in data["data"]:
            album_id = song["album"]["id"]
            time = dt.utcfromtimestamp(song["timestamp"]) + td(hours=dif)
            
            if time.date() != date_to_filter:
                # Continue to the next iteration if the dates are different from the given day.
                continue

            # Only the data from a given day.
            song_dict["song_name"].append(song["title"])
            song_dict["artist_name"].append(song["artist"]["name"])
            song_dict["timestamp"].append(time)
            song_dict["date"].append(time.date())
            try:
                r = requests.get(f"https://api.deezer.com/album/{album_id}")
                r.raise_for_status()
                genres = r.json()
                song_dict["genre"].append(genres["genres"]["data"][0]["name"])
            except requests.exceptions.HTTPError as e:
                raise SystemExit(e)
            except requests.exceptions.RequestException as e:
                raise SystemExit(e)
            except IndexError:
                song_dict["genre"].append("n/a")

def validation_data(df):
    # check if DataFrame is empty
    if df.empty:
        raise SystemExit("No tracks available for download. Finishing execution")
    # primary key check
    if not pd.Series(df["timestamp"]).is_unique:
        raise Exception("Primary Key Check Failed")
    # check for nulls
    if df.isnull().values.any():
        raise Exception("Null valued found")
    return True


# Extract

# initializes a dictionary storing the data
song_dict = {
    "song_name": [],
    "artist_name": [],
    "genre": [],
    "timestamp": [],
    "date": [],
}

# call api_token and create history data
api_token = os.getenv("API_TOKEN")
history = get_history(user_id, api_token)

# checks if the api token is valid, if not, calls the get_token function
try:
    fill_dict(song_dict, history)
except KeyError:
    get_token()
    load_dotenv(override=True)
    api_token = os.getenv("API_TOKEN")
    history = get_history(user_id, api_token)
    fill_dict(song_dict, history)

# create a DataFrame
song_df = pd.DataFrame(
    song_dict, columns=["song_name", "artist_name", "genre", "timestamp", "date"]
)


# Validate

if validation_data(song_df):
    print("Data valid, proceed to Load stages")

# Load

conn = sqlite3.connect("my_tracks.sqlite")
cursor = conn.cursor()

sql_query = """
CREATE TABLE IF NOT EXISTS my_tracks(
    song_name VARCHAR(200),
    artist_name VARCHAR(200),
    genre VARCHAR(200),
    timestamp DATETIME,
    date DATE,
    CONSTRAINT primary_key_constraint PRIMARY KEY (timestamp)
)
"""

cursor.execute(sql_query)
print("Open database...")

try:
    song_df.to_sql("my_tracks", conn, index=False, if_exists="append")
    print(">>> updating data <<<")
except:
    print("Data already exists in the database")

conn.close()
print("...Close database")

# input('\nPress "ENTER" key to exit')
