import datetime
import sqlalchemy as sqla
from sqlalchemy import create_engine
import traceback
import glob
import os
#import py as MySQLdb
#from pprint import PPrint
#import simplejson as json
import requests
import time
import json

# secrets.py file where i store sensitive info
import my_secrets

from IPython.display import display

# mysql driver
import pymysql
WEATHERKEY = os.environ.get("WEATHERKEY")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_URL = os.environ.get("DB_URL")
#r = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat=53.3498&lon=-6.2603&appid={0}".format(WEATHERKEY))
#Connect to database
engine = create_engine("mysql+pymysql://{0}:{1}@{2}".format(DB_USER, DB_PASS, DB_URL), echo=True)
connection = engine.connect()

sql_create_table1 = """
CREATE TABLE IF NOT EXISTS `dublin_bikes`.`current` (
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

sql_create_table2 = """
CREATE TABLE IF NOT EXISTS `dublin_bikes`.`forcast` (
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

try:
    #res = engine.execute("DROP TABLE IF EXISTS `dublin_bikes`.`current`")
    res = engine.execute(sql_create_table1)
    print(res.fetchall())
except Exception as e:
    print(e)

try:
    #res = engine.execute("DROP TABLE IF EXISTS `dublin_bikes`.`forcast`")
    res = engine.execute(sql_create_table2)
    print(res.fetchall())
except Exception as e:
    print(e)

def get_data(data):
    now = datetime.datetime.utcnow()
    return (now, datetime.datetime.fromtimestamp(data.get("dt")), data.get("temp"), data.get("feels_like"), data.get("pressure"), data.get("humidity"), data.get("visibility"), data.get("wind_speed"), data.get("wind_deg"), data.get("weather")[0].get("main"), data.get("weather")[0].get("description"))


def current_weather(text):
    data = json.loads(text)
    current = data["current"]
    vals = get_data(current)
    engine.execute("INSERT INTO `dublin_bikes`.`current` values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", vals)
    return

def hour_weather(text):
    data = json.loads(text)
    hourly = data["hourly"]
    for hour in hourly:
        vals = get_data(hour)
        engine.execute("INSERT INTO `dublin_bikes`.`forcast` values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", vals)
    return


def main():
    print(os.path)
    while True:
        try:
            now = datetime.datetime.now()
            r = requests.get("https://api.openweathermap.org/data/2.5/onecall?lat=53.3498&lon=-6.2603&appid={0}".format(WEATHERKEY))
            print(r, now)
            current_weather(r.text)
            hour_weather(r.text)
            time.sleep(5 * 60)
        except:
            print(traceback.format_exc())
            print("Error found an error when querying")
            time.sleep(5 * 60)
            # if engine is None:
            # pass


if __name__ == "__main__":
    main()