#!/usr/bin/env python
# coding: utf-8

# api.openweathermap.org/data/2.5/forecast/daily?lat={lat}&lon={lon}&cnt={cnt}&appid={API key}

# By geographic coordinates
# You can seach 16 day weather forecast with daily average parameters by geographic coordinats. All weather data can be obtained in JSON and XML formats.

# In[1]:


import datetime
import sqlalchemy as sqla
from sqlalchemy import create_engine
import traceback
import glob
import os
import requests
import time
import json


# In[2]:


# secrets.py file where i store sensitive info
import my_secrets


# In[3]:


# mysql driver
import pymysql


# In[4]:


# initialise environment variables
WEATHERKEY = os.environ.get("WEATHERKEY")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_URL = os.environ.get("DB_URL")


# In[5]:


# variables to scrape forecast every half an hour
forecast_max = 16
forecast_count = forecast_max


# In[6]:


# create connection to database using environment variables
# initialise as global variable so all functions can use it
print(DB_USER, DB_PASS, DB_URL)
engine = create_engine("mysql+pymysql://{0}:{1}@{2}".format(DB_USER, DB_PASS, DB_URI), echo=True)
connection = engine.connect()
print(os.path)
print(os.path.abspath(os.getcwd()))


# In[7]:


# print(os.path)
# print(os.path.abspath(os.getcwd()))
# print(DB_USER)
# print(DB_PASS)
# print(DB_URI)


# In[8]:


# 16 day weather forcast table 
sql_create_table_weather_current = """
CREATE TABLE IF NOT EXISTS `dublin_bikes`.`weather_16DayFcast` (
time_queried DATETIME,
last_update DATETIME,
temp_day FLOAT,
temp_night FLOAT,
temp_eve FLOAT,
temp_morn FLOAT,
feels_like_day FLOAT,
feels_like_night FLOAT,
feels_like_eve FLOAT,
feels_like_morn FLOAT,
pressure FLOAT,
humidity FLOAT,
weather_main VARCHAR(256),
weather_description VARCHAR(256),
speed FLOAT,
deg FLOAT,
clouds FLOAT,
pop FLOAT
)
"""


# In[9]:


# try to create both tables
def create_table():
    """
    Function to create 16 day table
    Only needs to be run once
    """
    try:
        res = engine.execute("DROP TABLE IF EXISTS `dublin_bikes`.`weather_16DayFcast`")
        res = engine.execute(sql_create_table_weather_current)
        print(res.fetchall())
    except Exception as e:
        print(e)


# In[10]:


def get_data(data):
    """
    this function takes in the data and station number as input and returns a tuple with that data
    """
    now = datetime.datetime.utcnow()
    
    return (now, datetime.datetime.fromtimestamp(data.get("dt")), data.get("temp").get("day"), data.get("temp").get("night"),            data.get("temp").get("eve"), data.get("temp").get("morn"),data.get("feels_like").get("day"), data.get("feels_like").get("night"),            data.get("feels_like").get("eve"), data.get("feels_like").get("morn"), data.get("pressure"), data.get("humidity"),            data.get("weather")[0].get("main"), data.get("weather")[0].get("description"),            data.get("speed"), data.get("deg"), data.get("clouds"), data.get("pop"))


# In[12]:


'''CHANGE 1 FROM MY SECRETS'''

def SixteenDay():
    """
    Gets 16 day weather forecast and imports into the data to database
    """
    print(WEATHERKEY)
    r = requests.get(f"https://api.openweathermap.org/data/2.5/forecast/daily?lat=53.344004&lon=-6.26812&cnt=16&appid={WEATHERKEY}")
    data = json.loads(r.text)
    days = data.get("list")
    print(data)
                     
    for day in days:
        vals = get_data(day) # get data function returns tuple of values
        print(vals)
        engine.execute("INSERT INTO `dublin_bikes`.`weather_16DayFcast` values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", vals)
    return


# In[ ]:


def main():
    global forecast_count
    # run create tables once
    # create_table()
    #print(os.path)
    while True:
        try:
            SixteenDay()
            # forecast_count += 1
            time.sleep(60 * 60 * 24)
        except:
            print(traceback.format_exc())
            print("Error found an error when querying")
            time.sleep(60 * 60 * 24)
            # if engine is None:
            # pass

if __name__ == "__main__":
    main()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




