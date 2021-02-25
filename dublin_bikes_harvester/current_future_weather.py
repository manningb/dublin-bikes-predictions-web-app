import datetime
import sqlalchemy as sqla
from sqlalchemy import create_engine
import traceback
import glob
import os
import requests
import time
import json

# secrets.py file where i store sensitive info
# import my_secrets

#from IPython.display import display

# mysql driver
import pymysql

# initialise environment variables
WEATHERKEY = os.environ.get("WEATHERKEY")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_URL = os.environ.get("DB_URL")
forecast_count = 6
# create connection to database using environment variables
# initialise as global variable so all functions can use it
print(DB_USER, DB_PASS, DB_URL)
engine = create_engine("mysql+pymysql://{0}:{1}@{2}".format(DB_USER, DB_PASS, DB_URL), echo=True)
connection = engine.connect()

# create current weather forecast table
sql_create_table_weather_current = """
CREATE TABLE IF NOT EXISTS `dublin_bikes`.`weather_current` (
station_number INTEGER,
time_queried DATETIME,
last_update DATETIME,
temp INTEGER,
feels_like INTEGER,
pressure INTEGER,
humidity INTEGER,
visibility INTEGER,
wind_speed INTEGER,
wind_deg INTEGER,
weather_main VARCHAR(256),
weather_description VARCHAR(256)
)
"""

# create 1 hourly weather forecast table
sql_create_forecast_1hour = """
CREATE TABLE IF NOT EXISTS `dublin_bikes`.`weather_forecast_1hour` (
station_number INTEGER,
time_queried DATETIME,
last_update DATETIME,
temp INTEGER,
feels_like INTEGER,
pressure INTEGER,
humidity INTEGER,
visibility INTEGER,
wind_speed INTEGER,
wind_deg INTEGER,
weather_main VARCHAR(256),
weather_description VARCHAR(256)
)
"""

# try to create both tables
def create_tables():
    """
    Function to create tables
    Only needs to be run once
    """
    try:
        res = engine.execute("DROP TABLE IF EXISTS `dublin_bikes`.`weather_current`")
        res = engine.execute(sql_create_table_weather_current)
        print(res.fetchall())
    except Exception as e:
        print(e)

    try:
        res = engine.execute("DROP TABLE IF EXISTS `dublin_bikes`.`weather_forecast_1hour`")
        res = engine.execute(sql_create_forecast_1hour)
        print(res.fetchall())
    except Exception as e:
        print(e)


def get_data(data, station_number):
    """
    this function takes in the data and station number as input and returns a tuple with that data
    """
    now = datetime.datetime.utcnow()
    return (station_number, now, datetime.datetime.fromtimestamp(data.get("dt")), data.get("temp"), data.get("feels_like"), data.get("pressure"), data.get("humidity"), data.get("visibility"), data.get("wind_speed"), data.get("wind_deg"), data.get("weather")[0].get("main"), data.get("weather")[0].get("description"))


def loop_through_stations(text):
    """
    loops through each of the stations in the dublin bikes static data
    stores relevant values in response to variables
    requests data from Open Weather Map API and import this data to the database
    takes an input text file of Dublin Bikes stations
    """
    global forecast_count
    stations = json.loads(text)
    # loop through each dublin bikes station
    for station in stations:
        # print out name for debugging
        print(station.get("name"))

        # get dublin bikes variables
        station_number = station.get("number")
        station_lng = station.get("position").get("lng")
        station_lat = station.get("position").get("lat")
        r = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat={station_lat}&lon={station_lng}&appid={WEATHERKEY}")

        #print out the time
        # to be used in the debug logs
        now = datetime.datetime.now()
        print(r, now)
        current_weather(r.text, station_number)
        # if the script has ran 6 times, do hourly forecast
        # this occurs every half an hour
        if forecast_count >= 6:
            hour_weather(r.text, station_number)

    # need to check outside of for loop so whole loop runs
    if forecast_count >= 6:
        forecast_count = 0 # reset to 0

def current_weather(text, station_number):
    """
    Gets current weather and imports the data to database
    """
    data = json.loads(text)
    current = data["current"]
    vals = get_data(current, station_number) # get data function returns tuple of values
    engine.execute("INSERT INTO `dublin_bikes`.`weather_current` values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", vals)
    return

def hour_weather(text, station_number):
    """
    Gets hourly weather from the one call api
    Imports this data to the database
    """
    data = json.loads(text)
    hourly = data["hourly"]

    # loop through each hour
    for hour in hourly:
        vals = get_data(hour, station_number) # get data function returns tuple of values
        engine.execute("INSERT INTO `dublin_bikes`.`weather_forecast_1hour` values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", vals)
    return

def get_dublin_bikes_stations():
    # API Key for Dublin Bikes JCDecaux
    DubBike_API = os.environ.get("API_DubBike")
    DubBike_NAME = "Dublin"
    DubBike_STATIONS = "https://api.jcdecaux.com/vls/v1/stations/"
    DubBikes_r = requests.get(DubBike_STATIONS, params={"apiKey": DubBike_API, "contract": DubBike_NAME})
    print(DubBikes_r)
    return DubBikes_r

def main():
    global forecast_count
    # run create tables once
    create_tables()
    #print(os.path)

    # set count variable = 30
    # we want forecast data to be fetched every half an hour

    while True:
        try:
            stations = get_dublin_bikes_stations().text
            loop_through_stations(stations)
            forecast_count += 1
            time.sleep(5 * 60)
        except:
            print(traceback.format_exc())
            print("Error found an error when querying")
            time.sleep(5 * 60)
            # if engine is None:
            # pass

if __name__ == "__main__":
    main()