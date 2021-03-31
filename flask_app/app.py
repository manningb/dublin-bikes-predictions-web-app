import datetime
import os

from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine

app = Flask("__name__", template_folder="templates")

# global variables used for caching
global last_updated_availability_time, last_updated_weather_time
last_updated_availability_time = datetime.datetime.now()
last_updated_weather_time = datetime.datetime.now()
global last_updated_availability_data, last_updated_weather_data
global first_run_availability, first_run_weather
first_run = True
first_run_weather = True


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
    global last_updated_availability_time, last_updated_availability_data, first_run
    if ((last_updated_availability_time - datetime.datetime.now()).total_seconds() > 900 or first_run):
        first_run = False
        sql_get_availability = """select db_a.number, position_lat, position_lng, name, address, available_bikes, available_bike_stands, max(db_a.last_update) as last_update
    FROM dublin_bikes.station db_s
    INNER JOIN dublin_bikes.availability db_a ON
    db_s.number = db_a.number
    GROUP BY number
    """  # create select statement for stations table

        rows = sql_query(sql_get_availability)  # execute select statement

        last_updated_availability_data = []
        for row in rows:
            last_updated_availability_data.append(dict(row))  # inset dict of data into list
            print(row)
    last_updated_availability_time = datetime.datetime.now()
    return jsonify(station=last_updated_availability_data)  # return json string of data


@app.route("/current_weather")
def current_weather():
    """
    Get all stations
    render template to client
    """
    global last_updated_weather_time, last_updated_weather_data, first_run_weather
    if ((last_updated_weather_time - datetime.datetime.now()).total_seconds() > 900 or first_run_weather):
        first_run_weather = False
        sql_get_weather = """SELECT *
        FROM dublin_bikes.weather_current 
        ORDER  BY last_update DESC
        LIMIT  1;
            """

        rows = sql_query(sql_get_weather)
        last_updated_weather_data = []
        for row in rows:
            last_updated_weather_data.append(dict(row))  # inset dict of data into list
            print(row)
    last_updated_weather_time = datetime.datetime.now()
    return jsonify(weather=last_updated_weather_data)  # return json string of data


if __name__ == "__main__":
    # default port is 5000 if you don't specify
    app.run(debug=True, port=5000)
