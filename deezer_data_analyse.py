import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

db = "./my_tracks.sqlite"

conn = sqlite3.connect(db)

sql_query = "SELECT * FROM my_tracks"
df = pd.read_sql(sql_query, conn)

df["genre"] = df["genre"].astype("category")
df["artist_name"] = df["artist_name"].astype("category")
df["timestamp"] = df["timestamp"].astype("datetime64")
df["date"] = df["date"].astype("datetime64")

most_track = df.song_name.value_counts().index[0]
most_track_artist = df[df.song_name == most_track]["artist_name"].iloc[0]
most_artist = df.artist_name.value_counts().index[0]
most_day = df.date.value_counts().index[0].date()
summary_dict = {
    "total number of tracks": len(df),
    "the most played track": f"{most_track} by {most_track_artist}",
    "the most played artist": most_artist,
    "the day with the most tracks": f'{most_day}, {most_day.strftime("%A")}',
}

summary = pd.DataFrame.from_dict(summary_dict, orient="index", columns=["Summary"])
print(summary, "\n")

genre_min = df["genre"].value_counts() > 20
genre = df.genre.value_counts()[genre_min]
labels = genre.index

artist_by_genre = {}
group_genre = df.groupby("genre")
for label in labels:
    artist_by_genre[label] = (
        group_genre.get_group(label).artist_name.value_counts().index[0]
    )


summary_by_genre = pd.DataFrame.from_dict(
    artist_by_genre, orient="index", columns=["the most played artist by genre"]
)
print(summary_by_genre)


plt.pie(genre, labels=labels)
plt.title("favorite genre")
plt.savefig("./sample/sample_genre.jpg", bbox_inches="tight")
plt.close()


df["hour"] = df.apply(lambda row: row.timestamp.hour, axis=1)
df["day"] = df.apply(lambda row: row.date.day_name(), axis=1)


plt.hist(df.hour, bins=range(0, 24), ec="black")
plt.ylabel("songs played")
plt.title("distribution of songs during the day")
plt.savefig("./sample/sample_day.jpg", bbox_inches="tight")
plt.close()


cats = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
df["day"] = pd.Categorical(df["day"], categories=cats, ordered=True)
df_d = df.sort_values("day")


plt.hist(df_d.day, bins=range(0, 8), ec="black")
plt.ylabel("songs played")
plt.title("distribution of songs during the week")
plt.xticks(rotation=45, ha="left")
plt.savefig("./sample/sample_week.jpg", bbox_inches="tight")
plt.close()
