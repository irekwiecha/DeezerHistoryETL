# Deezer History ETL
> Data pipeline using Deezer API. Download the data and save it in a SQLite database on local machine. 

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Project Status](#project-status)
* [Acknowledgements](#acknowledgements)
* [Contact](#contact)

## General Information
> This feed will run daily (need to add the script to the task schedule), and it will download the data about the tracks that you listened to during a day, and save that data in a SQLite database on your local machine. Before you can use this tool, you first need to declare your Deezer app in their developer portal: https://developers.deezer.com/myapps/create. Create a new app with the following Redirect URL: http://localhost:8080/oauth/return this is necessary for the `deezer-oauth-cli` package to work.
>INFO:
>As deezer API data is limited to the last 100 songs. The script is scheduled to run daily at the beginning of the day and download the songs from the previous day. If you want to run the script at the end of the day, change the `DAYS_TO_FILTER to 0` variable.

## Technologies Used
- Python 3.10
- Packages to install: *requests, pandas, deezer-oauth-cli, python-dotenv*
*all used packages in pipfile*

## Project Status
**Project is:** *in progress*
- [x] *implement EXTRACT*
- [x] *add README*
- [x] *add LICENSE (MIT)*
- [ ] *implement TRANSFORM*
- [ ] *implement LOAD*

## Job scheduling
> To run a script automatically, you can create a batch file and add it to the Task Scheduler

## Acknowledgements
- the project uses Deezer OAuth CLI from [Bruno Alla](https://github.com/browniebroke/deezer-oauth-cli)
- This project was based on one of the course from [Karolina Sowinska](https://www.youtube.com/c/KarolinaSowinska)

## Contact
Created by [@irekwiecha](https://github.com/irekwiecha)