import pandas as pd
import sqlalchemy as sqla 
from sqlalchemy import create_engine 
import pymysql
import my_secrets

engine = create_engine("mysql+pymysql://{0}:{1}@{2}".format(my_secrets.DB_USER, my_secrets.DB_PASS, my_secrets.DB_URI), echo=True) 
connection = engine.connect()

# create historical data table
sql_create_table = """
CREATE TABLE IF NOT EXISTS `dublin_bikes`.`historical_availability` (
number INTEGER,
available_bikes INTEGER,
available_bike_stands INTEGER,
last_update INTEGER,
station_status VARCHAR(20),
PRIMARY KEY (number, last_update)
)
"""

try:
    res = engine.execute(sql_create_table)
    print(res.fetchall())
except Exception as e:
    print(e)

# read in the historical data file from a csv
df = pd.read_csv('C:\\Users\\manni\\Documents\\ComputerScience\\College\\Semester 2\\30830 Software Engineering\\assignments\\a2 dublin_bikes\\data\\2020q4.csv')
df_renamed = df.rename(columns={'STATION ID': 'number', 'AVAILABLE BIKES': 'available_bikes', 'AVAILABLE BIKE STANDS':'available_bike_stands','LAST UPDATED':'last_update', 'STATUS':'station_status'})
df_renamed.drop(['TIME', 'NAME','BIKE STANDS','ADDRESS','LATITUDE','LONGITUDE'], axis = 1, inplace = True) 
print(df_renamed.dtypes)

# import data to sql
df_renamed.to_sql('dublin_bikes.historical_availability', con=engine, if_exists='replace')
