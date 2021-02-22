import sqlalchemy as sqla
from sqlalchemy import create_engine
import pymysql
import os

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_URL = os.environ.get("DB_URL")

#Connect to database
engine = create_engine("mysql+pymysql://{0}:{1}@{2}".format(DB_USER, DB_PASS, DB_URL), echo=True)
connection = engine.connect()

sql_create_schema = "CREATE SCHEMA `dublin_bikes`;"

try:
    res = engine.execute(sql_create_schema)
    print(res.fetchall())
except Exception as e:
    print(e)


# command to create table in mysql
sql_create_table = """
CREATE TABLE IF NOT EXISTS `dublin_bikes`.`station` (
address VARCHAR(256),
banking INTEGER,
bike_stands INTEGER,
bonus INTEGER,
contact_name VARCHAR(256),
name VARCHAR(256),
number INTEGER,
position_lat REAL,
position_lng REAL,
PRIMARY KEY (number)
)
"""

try:
    res = engine.execute("DROP TABLE IF EXISTS `dublin_bikes`.`station`")
    res = engine.execute(sql_create_table)
    print(res.fetchall())
except Exception as e:
    print(e)

# command to create table in mysql
sql_create_table = """
CREATE TABLE IF NOT EXISTS `dublin_bikes`.`availability` (
number INTEGER,
available_bikes INTEGER,
available_bike_stands INTEGER,
last_update INTEGER,
station_status VARCHAR(20),
time_queried DATETIME,
PRIMARY KEY (number, time_queried)
)
"""

try:
    res = engine.execute("DROP TABLE IF EXISTS `dublin_bikes`.`availability`")
    res = engine.execute(sql_create_table)
    print(res.fetchall())
except Exception as e:
    print(e)