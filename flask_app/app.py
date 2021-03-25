from flask import Flask, render_template, jsonify
import json
import os
from sqlalchemy import create_engine
import os
import requests
import json

app = Flask("__name__", template_folder="templates")


@app.route("/")
def index():
    GMAP_API = "AIzaSyDX7gu_rKXux6P20MBh1ThL3FfOKoGH64Q"
    return render_template("index.html", GMAP_API=GMAP_API)


@app.route("/stations")
def static_bikes():
    """
    Get all stations
    render template to client
    """
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_URL = os.environ.get("DB_URL")

    engine = create_engine("mysql+pymysql://{0}:{1}@{2}/dublin_bikes".format(DB_USER, DB_PASS, DB_URL), echo=True)
    connection = engine.connect()

    sql_create_schema = """select db_a.number, position_lat, position_lng, name, address, available_bikes, available_bike_stands, max(db_a.last_update) as last_update, weather.station_number, weather.weather_main
FROM dublin_bikes.station db_s
INNER JOIN dublin_bikes.availability db_a ON
db_s.number = db_a.number
INNER JOIN (
    SELECT weather_main, station_number, max(last_update)
    FROM weather_current
    group by station_number) weather ON weather.station_number =  db_a.number
GROUP BY number
"""  # create select statement for stations table

    rows = engine.execute(sql_create_schema)  # execute select statement

    stations = []
    for row in rows:
        stations.append(dict(row))  # inset dict of data into list
        print(row)
    return jsonify(station=stations)  # return json string of data


if __name__ == "__main__":
    # default port is 5000 if you don't specify
    app.run(debug=True, port=5000)
