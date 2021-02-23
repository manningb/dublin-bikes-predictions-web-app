import pandas as pd
import sqlalchemy as sqla 
from sqlalchemy import create_engine 
import pymysql
import os

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_URL = os.environ.get("DB_URL")
DB_PORT = os.environ.get("DB_PORT")

engine = create_engine("mysql+pymysql://{0}:{1}@{2}/dublin_bikes".format(my_secrets.DB_USER, my_secrets.DB_PASS, my_secrets.DB_URI), echo=True) 
connection = engine.connect()

#csvs of data by quarter from 2020Q1 - Q4
# from here: https://data.gov.ie/dataset/33ec9fe2-4957-4e9a-ab55-c5e917c7a9ab
quarters_csvs = ["https://data.smartdublin.ie/dataset/33ec9fe2-4957-4e9a-ab55-c5e917c7a9ab/resource/aab12e7d-547f-463a-86b1-e22002884587/download/dublinbikes_20200101_20200401.csv", "https://data.smartdublin.ie/dataset/33ec9fe2-4957-4e9a-ab55-c5e917c7a9ab/resource/8ddaeac6-4caf-4289-9835-cf588d0b69e5/download/dublinbikes_20200401_20200701.csv", "https://data.smartdublin.ie/dataset/33ec9fe2-4957-4e9a-ab55-c5e917c7a9ab/resource/99a35442-6878-4c2d-8dff-ec43e91d21d7/download/dublinbikes_20200701_20201001.csv", "https://data.smartdublin.ie/dataset/33ec9fe2-4957-4e9a-ab55-c5e917c7a9ab/resource/5328239f-bcc6-483d-9c17-87166efc3a1a/download/dublinbikes_20201001_20210101.csv"]

# loop through each quarter, format the data and add it to the database
for csv in quarters_csvs:
    df = pd.read_csv(csv)
    df_renamed = df.rename(columns={'STATION ID': 'number', 'AVAILABLE BIKES': 'available_bikes', 'AVAILABLE BIKE STANDS':'available_bike_stands','LAST UPDATED':'last_update', 'STATUS':'station_status'})
    df_renamed.drop(['TIME', 'NAME','BIKE STANDS','ADDRESS','LATITUDE','LONGITUDE'], axis = 1, inplace = True) 
    df_renamed.to_sql('historical_availability', index=False, con=engine, dtype={'number': sqla.types.Integer, 'available_bikes':sqla.types.Integer, 'available_bike_stands':sqla.types.Integer, 'last_update':sqla.types.DATETIME, 'station_status':sqla.types.String(length=20)}, if_exists='append')
