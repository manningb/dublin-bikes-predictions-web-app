import requests
import traceback
import datetime
import sqlalchemy as sqla 
from sqlalchemy import create_engine 
import time
import os
#import my_secrets
import pymysql
import json


os.get

NAME="Dublin"
STATIONS="https://api.jcdecaux.com/vls/v1/stations/"

#Connect to database
engine = create_engine("mysql+pymysql://{0}:{1}@{2}".format(my_secrets.DB_USER, my_secrets.DB_PASS, my_secrets.DB_URI), echo=True) 

def write_to_file(text):
    pass
    # date_underscores = "{:%Y_%m_%d_%H_%M_%S}".format(datetime.datetime.now())
    # with open(r"data\bikes_{}".format(date_underscores).replace(" ", "_"), "w") as f:
    #     f.write(text)

def stations_to_db(text):
    stations = json.loads(text)
    print(type(stations), len(stations))
    for station in stations:
        print(station)
        vals = (station.get("address"),int(station.get("banking")), int(station.get("bike_stands")), int(station.get("bonus")),station.get("contract_name"), station.get("name"), station.get("number"), station.get("position").get("lat"), station.get("position").get("lng"), station.get("status"))
        engine.execute("INSERT INTO `dublin_bikes`.`station` values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", vals)
    return

                                            
def main():
    print(os.path)
    while True:
        try:
            now = datetime.datetime.now()
            r = requests.get(STATIONS, params={"apiKey": my_secrets.APIKEY, "contract" : NAME})
            print(r, now)
            write_to_file(r.text)
            stations_to_db(r.text)
            time.sleep(5*60)
        except:
            print(traceback.format_exc())
            #if engine is None:
                #pass
        return

if __name__== "__main__":
    main()