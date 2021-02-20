# Various Imports for Python
import json
import os
import requests
import traceback
import datetime
import time

# Imports for MySQL
import pymysql
from sqlalchemy import create_engine

def availability_to_db(text, engine):
    """
    Read in the dynamic data of each stations to the database
    This needs to be run every 5 minutes
    No return value
    """
    stations = json.loads(text)
    now = datetime.datetime.utcnow()
    for station in stations:
        print(station)
        vals = (int(station.get("number")), int(station.get("available_bikes")), int(station.get("available_bike_stands")), int(station.get("last_update")), station.get("status"), now)
        engine.execute("INSERT INTO `dublin_bikes`.`availability` values(%s,%s,%s,%s,%s,%s)", vals)
    return


def main():
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_URL = os.environ.get("DB_URL")
    DB_PORT = os.environ.get("DB_PORT")

    # API Key for Dublin Bikes JCDecaux
    DubBike_API = os.environ.get("API_DubBike")
    DubBike_NAME = "Dublin"
    DubBike_STATIONS = "https://api.jcdecaux.com/vls/v1/stations/"
    # Connect to database
    engine = create_engine("mysql+pymysql://{0}:{1}@{2}".format(DB_USER, DB_PASS, DB_URL), echo=True)

    # Send requests to get all static data, then write to db
    while True:
        try:
            r = requests.get(DubBike_STATIONS, params={"apiKey": DubBike_API, "contract": DubBike_NAME})
            availability_to_db(r.text, engine)
            time.sleep(5 * 60)
        except:
            print(traceback.format_exc())

        return

if __name__== "__main__":
    main()