# Deezer History ETL
Simple data pipeline using Deezer API. Download the data and save it in a SQLite database on local machine. 

## General Information
This feed will run daily (need to add the script to the task schedule), and it will download the data about the tracks that you listened to during a day, and save that data in a SQLite database on your local machine. Before you can use this tool, you first need to declare your Deezer app in their developer portal: https://developers.deezer.com/myapps/create. Create a new app with the following Redirect URL: http://localhost:8080/oauth/return this is necessary for the `deezer-oauth-cli` package to work.

As deezer API data is limited to the last 100 songs. The script is scheduled to run daily at the beginning of the day and download the songs from the previous day. If you want to run the script at the end of the day, change the `DAYS_TO_FILTER to 0` variable.

## Features
The generated database contains the following information:
- Song name
- Artist name
- Genre
- Timestamp `YYYY-MM-DD hh:mm:ss`
- Date `YYYY-MM-DD`

## Tech Stack
- Python 3.10
- Packages to install: *requests, pandas, deezer-oauth-cli, python-dotenv*

## Job scheduling
To run a script automatically, you can create a batch file and add it to the Task Scheduler

## Acknowledgements
- the project uses Deezer OAuth CLI from [Bruno Alla](https://github.com/browniebroke/deezer-oauth-cli)
- This project was based on one of the course from [Karolina Sowinska](https://www.youtube.com/c/KarolinaSowinska)

## Authors
Created by [@irekwiecha](https://github.com/irekwiecha)