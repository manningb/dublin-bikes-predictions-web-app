from flask import Flask, render_template, jsonify
import json
import os
from sqlalchemy import create_engine
import os
import requests
import json
import pandas as pd
import decimal
import joblib
app = Flask("__name__", template_folder="templates")

@app.route("/")
def index():
    GMAP_API = "AIzaSyDX7gu_rKXux6P20MBh1ThL3FfOKoGH64Q"
    return render_template("index.html", GMAP_API=GMAP_API)

    return render_template("stationstats.html", NUMBER=number)


@app.route("/stationstats-<int:number>")
def stationstats(number):
    return render_template("stationstats.html", NUMBER=number)

def sql_query(query):
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_URL = os.environ.get("DB_URL")
    engine = create_engine("mysql+pymysql://{0}:{1}@{2}/dublin_bikes".format(DB_USER, DB_PASS, DB_URL), echo=True)
    connection = engine.connect()

    rows = engine.execute(query)
    return rows

@app.route("/hour48-<int:number>")
def hour48(number):
    model = joblib.load('../data_analytics/station-2.pkl')
    features = ['temp',  'humidity', 'wind_speed', 'dayquery_Friday', 'dayquery_Monday', 'dayquery_Saturday', 'dayquery_Sunday', 'dayquery_Thursday',
 'dayquery_Tuesday', 'dayquery_Wednesday', 'weather_main_Clear', 'weather_main_Clouds', 'weather_main_Drizzle', 'weather_main_Fog', 'weather_main_Mist', 'weather_main_Rain']

    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_URL = os.environ.get("DB_URL")

    engine = create_engine("mysql+pymysql://{0}:{1}@{2}".format(DB_USER, DB_PASS, DB_URL), echo=True)
    connection = engine.connect()

    statement = """SELECT last_update, dayname(last_update) as dayquery, hour(last_update) as hourquery, temp, humidity, wind_speed, weather_main FROM dublin_bikes.weather_forecast_1hour
    where station_number = 2
    order by time_queried
    limit 48;"""
    df_future = pd.read_sql_query(statement, engine)
    categorical_columns = df_future[['dayquery', 'hourquery', 'weather_main', 'dayquery', 'hourquery']].columns
    # Convert data type to category for these columns
    for column in categorical_columns:
        df_future[column] = df_future[column].astype('category')

    df_future["humidity"] = df_future["humidity"].fillna(0)
    df_final_future = pd.get_dummies(df_future, drop_first=False)
    for col in features:
        if col not in df_final_future.columns:
            df_final_future[col] = [0 for i in range(len(df_final_future))]
    result = model.predict(df_final_future[features])
    dictionary = dict(zip(df_final_future["last_update"].astype(str).to_list(), result.tolist()))
    return jsonify(dictionary)

@app.route("/statstation-<int:number>")
def statstation(number):
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_URL = os.environ.get("DB_URL")

    engine = create_engine("mysql+pymysql://{0}:{1}@{2}/dublin_bikes".format(DB_USER, DB_PASS, DB_URL), echo=True)
    connection = engine.connect()

    sql_create_schema = f"""SELECT * FROM dublin_bikes.availability
where number = {number}
order by time_queried desc
limit 500;"""
    rows = engine.execute(sql_create_schema)  # execute select statement

    stations = []
    for row in rows:
        stations.append(dict(row))  # inset dict of data into list
        print(row)
    return jsonify(station=stations)  # return json string of data

@app.route("/averagestation-<int:number>")
def averagestation(number):
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_URL = os.environ.get("DB_URL")
    engine = create_engine("mysql+pymysql://{0}:{1}@{2}/dublin_bikes".format(DB_USER, DB_PASS, DB_URL), echo=True)
    connection = engine.connect()
    sql_create_schema = f"""SELECT cast(avg(available_bikes) as char) as avgavailbikes, cast(avg(available_bike_stands) as char)as avgavailbikestation, Year(time_queried) as yearq, month(time_queried) as monthq, day(time_queried) as dateq FROM dublin_bikes.availability
where number = {number}
group by date(time_queried)
order by time_queried desc;"""

    rows = engine.execute(sql_create_schema)  # execute select statement

    stations = []
    for row in rows:
        stations.append(dict(row))  # inset dict of data into list
        print(row)
    print(stations)
    return jsonify(stations)

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

if __name__ == "__main__":
    # default port is 5000 if you don't specify
    app.run(debug=True, port=5000)
