import os
import requests
import unittest
import pytest
from sqlalchemy import create_engine


DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_URL = os.environ.get("DB_URL")
DB_PORT = os.environ.get("DB_PORT")

# API Key for Dublin Bikes JCDecaux
DubBike_API = os.environ.get("API_DubBike")
DubBike_NAME = "Dublin"
DubBike_STATIONS = "https://api.jcdecaux.com/vls/v1/stations/"
# Connect to database


def test_database_connection():
    """
    Testing the conenction to the database, available bikes table
    """
    engine = create_engine("mysql+pymysql://{0}:{1}@{2}".format(DB_USER, DB_PASS, DB_URL), echo=True)
    connection = engine.connect()
    sql_create_schema = f"""SELECT * FROM dublin_bikes.availability
    where number = 2
    order by time_queried asc
    limit 1;"""
    rows = engine.execute(sql_create_schema)  # execute select statement
    connection.close()
    engine.dispose()
    stations = []
    for row in rows:
        stations.append(dict(row))  # inset dict of data into list
    assert len(stations) == 1

def test_database_weather():
    """
    Testing the conenction to the database, current weather table
    """
    engine = create_engine("mysql+pymysql://{0}:{1}@{2}".format(DB_USER, DB_PASS, DB_URL), echo=True)
    connection = engine.connect()
    sql_create_schema = f"""SELECT *
        FROM dublin_bikes.weather_current 
        ORDER  BY last_update DESC
        LIMIT  1;
            """
    rows = engine.execute(sql_create_schema)  # execute select statement
    connection.close()
    engine.dispose()
    stations = []
    for row in rows:
        stations.append(dict(row))  # inset dict of data into list
    assert len(stations) == 1


if __name__ == '__main__':
    unittest.main(argv=['ignored', '-v'], exit=False)
