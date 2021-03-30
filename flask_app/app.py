from flask import Flask, render_template, jsonify
import json
import os
from sqlalchemy import create_engine
import os
import requests
import json
from math import cos, sqrt
import geopy.distance

app = Flask("__name__", template_folder="templates")

@app.route("/")
def index():
    GMAP_API = "AIzaSyDX7gu_rKXux6P20MBh1ThL3FfOKoGH64Q"
    return render_template("index.html", GMAP_API=GMAP_API)

def sql_query(query):
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_URL = os.environ.get("DB_URL")

    engine = create_engine("mysql+pymysql://{0}:{1}@{2}/dublin_bikes".format(DB_USER, DB_PASS, DB_URL), echo=True)
    connection = engine.connect()

    rows = engine.execute(query)
    return rows

@app.route("/stations")
def static_bikes():
    """
    Get all stations
    render template to client
    """
    sql_get_availability = """select db_a.number, position_lat, position_lng, name, address, available_bikes, available_bike_stands, max(db_a.last_update) as last_update
FROM dublin_bikes.station db_s
INNER JOIN dublin_bikes.availability db_a ON
db_s.number = db_a.number
GROUP BY number
"""  # create select statement for stations table

    rows = sql_query(sql_get_availability)  # execute select statement

    stations = []
    for row in rows:
        stations.append(dict(row))  # inset dict of data into list
        print(row)
    return jsonify(station=stations)  # return json string of data

@app.route("/current_weather")
def current_weather():
    """
    Get all stations
    render template to client
    """
    sql_get_weather = """SELECT *
    FROM dublin_bikes.weather_current 
    ORDER  BY last_update DESC
    LIMIT  1;
        """

    rows = sql_query(sql_get_weather)
    weather = []
    for row in rows:
        weather.append(dict(row))  # inset dict of data into list
        print(row)
    return jsonify(weather=weather)  # return json string of data


@app.route("/find_now/lat=<lat>&lng=<lng>/<bike_or_station>")
def find_now(lat, lng, bike_or_station):
    """
Find bike or station near location now
    """
    sql_get_closest = """select db_a.number, position_lat, position_lng, name, address, available_bikes, available_bike_stands, max(db_a.last_update) as last_update
FROM dublin_bikes.station db_s
INNER JOIN dublin_bikes.availability db_a ON
db_s.number = db_a.number
GROUP BY number
"""  # create select statement for stations table
    rows = sql_query(sql_get_closest)  # execute select statement

    stations = []
    for row in rows:
        stations.append(dict(row))  # inset dict of data into list
        print(row)

    sorted_stations = sorted(stations, key=lambda d: distance(d["position_lng"], d["position_lat"], lat, lng))
    #
    # print(sorted_stations[5])
    for i in sorted_stations:
        print(i)
    print(lat, lng)
    return jsonify(sorted_stations=sorted_stations[0])  # return json string of data




def distance(lon1, lat1, lon2, lat2):
    arguments = (lon1, lat1, lon2, lat2)
    lon1, lat1, lon2, lat2 = map(float, arguments)
    distance = geopy.distance.vincenty((lat1, lon1), (lat2, lon2)).km
    return distance


if __name__ == "__main__":
    # default port is 5000 if you don't specify
    app.run(debug=True, port=5000)
