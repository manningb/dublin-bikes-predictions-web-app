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
# create connection to database using environment variables
# initialise as global variable so all functions can use it
print(DB_USER, DB_PASS, DB_URL)
engine = create_engine("mysql+pymysql://{0}:{1}@{2}".format(DB_USER, DB_PASS, DB_URL), echo=True)
connection = engine.connect()

# create current weather forecast table
sql_create_table_historical_daily = """
CREATE TABLE IF NOT EXISTS `dublin_bikes`.`weather_historical_daily` (
time_queried DATETIME,
last_update DATETIME,
temp FLOAT,
feels_like FLOAT,
pressure FLOAT,
humidity FLOAT,
visibility FLOAT,
wind_speed FLOAT,
wind_deg FLOAT,
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
        res = engine.execute("DROP TABLE IF EXISTS `dublin_bikes`.`weather_historical_daily`")
        res = engine.execute(sql_create_table_historical_daily)
        print(res.fetchall())
    except Exception as e:
        print(e)


def get_data(data):
    """
    this function takes in the data and station number as input and returns a tuple with that data
    """
    now = datetime.datetime.utcnow()
    return (now, datetime.datetime.fromtimestamp(data.get("dt")), data.get("main").get("temp"), data.get("main").get("feels_like"), data.get("main").get("pressure"), data.get("main").get("humidity"), data.get("visibility"), data.get("wind").get("speed"), data.get("wind").get("deg"), data.get("weather")[0].get("main"), data.get("weather")[0].get("description"))


def loop_through_stations():
    """
    loops through each of the stations in the dublin bikes static data
    stores relevant values in response to variables
    requests data from Open Weather Map API and import this data to the database
    takes an input text file of Dublin Bikes stations
    """
    station_lng = -6.266802
    station_lat = 53.344007
    loop_through_2020_by_week(station_lng, station_lat, start_week=0, end_week=52)

def loop_through_2020_by_week(station_lng, station_lat, start_week, end_week):
    """
    Loops through all dates in 2020 by week as this is max api request
    """
    one_week = 604800 # one week in UTC
    # initialise the very start start of the script
    # this time represents 01/01/2020 00:00:00

    start_date = 1585138591 + (start_week * one_week)
    print(start_date)

    end_date = start_date + one_week
    for i in range(52):
        #payload = {'start_dat': start_date, 'key2': 'value2'}
        REQUEST = f"http://history.openweathermap.org/data/2.5/history/city?lat={station_lat}&lon={station_lng}&type=hour&start={start_date}&end={end_date}&appid={WEATHERKEY}"
        #print(REQUEST)
        r = requests.get(REQUEST)
        start_date = end_date
        end_date += one_week
        #print(r.text)
        data = json.loads(r.text)
        days = data.get("list")
        for day in days:
            print(day)
            vals = get_data(day)
            engine.execute("INSERT INTO `dublin_bikes`.`weather_historical_daily` values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",vals)
            print(vals)

def get_dublin_bikes_stations():
    # API Key for Dublin Bikes JCDecaux
    DubBike_API = os.environ.get("API_DubBike")
    DubBike_NAME = "Dublin"
    DubBike_STATIONS = "https://api.jcdecaux.com/vls/v1/stations/"
    DubBikes_r = requests.get(DubBike_STATIONS, params={"apiKey": DubBike_API, "contract": DubBike_NAME})
    print(DubBikes_r)
    return DubBikes_r

def main():
    # run create tables once
    create_tables()
    #print(os.path)
    try:
        #stations = get_dublin_bikes_stations().text
        loop_through_stations()
        time.sleep(5 * 60)
    except:
        print(traceback.format_exc())
        print("Error found an error when querying")
        time.sleep(5 * 60)
        # if engine is None:
        # pass

if __name__ == "__main__":
    main()