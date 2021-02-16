import requests
import traceback
import datetime
import time
import os
from api_keys import APIKEY

NAME="Dublin"
STATIONS="https://api.jcdecaux.com/vls/v1/stations/"

def write_to_file(text):
    date_underscores = "{:%Y_%m_%d_%H_%M_%S}".format(datetime.datetime.now())
    with open(r"data\bikes_{}".format(date_underscores).replace(" ", "_"), "w") as f:
        f.write(text)

def stations_to_db(text):
    stations = json.loads(text)
    print(type(stations), len(stations))
    for station in stations:
        print(station)
        vals = (station.get("address"))

def main():
    print(os.path)
    while True:
        try:
            now = datetime.datetime.now()
            r = requests.get(STATIONS, params={"apiKey": APIKEY, "contract" : NAME})
            print(r, now)
            write_to_file(r.text)
            time.sleep(5*60)
        except:
            print(traceback.format_exc())
            #if engine is None:
                #pass
        return

if __name__== "__main__":
    main()