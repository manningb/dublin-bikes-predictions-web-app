import datetime
import os

import joblib
import pandas as pd
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
    GMAP_API = os.environ.get("GMAP_API")
    return render_template("index.html", GMAP_API=GMAP_API)


@app.route("/statistics")
def statistics():
    return render_template("main_stats.html")


@app.route("/stationstats-<int:number>")
def stationstats(number):
    return render_template("stationstats.html", NUMBER=number)


def sql_query(query):
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_URL = os.environ.get("DB_URL")
    engine = create_engine(
        "mysql+pymysql://{0}:{1}@{2}/dublin_bikes".format(DB_USER, DB_PASS, DB_URL), echo=True)
    connection = engine.connect()

    rows = engine.execute(query)
    connection.close()
    engine.dispose()
    return rows


@app.route("/one_hour-<int:bike_station_num>-<int:day_num>-<int:hour_num>")
def one_hour(bike_station_num, day_num, hour_num):
    model = joblib.load(
        f'../data_analytics/pickles/station-{bike_station_num}')
    features = ['temp',  'humidity', 'wind_speed', 'dayquery_Friday', 'dayquery_Monday', 'dayquery_Saturday', 'dayquery_Sunday', 'dayquery_Thursday',
                'dayquery_Tuesday', 'dayquery_Wednesday', 'weather_main_Clear', 'weather_main_Clouds', 'weather_main_Drizzle', 'weather_main_Fog', 'weather_main_Mist', 'weather_main_Rain']

    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_URL = os.environ.get("DB_URL")

    engine = create_engine(
        "mysql+pymysql://{0}:{1}@{2}".format(DB_USER, DB_PASS, DB_URL), echo=True)
    connection = engine.connect()

    statement = f"""SELECT last_update, dayname(last_update) as dayquery, hour(last_update) as hourquery, temp, humidity, wind_speed, weather_main FROM dublin_bikes.weather_forecast_1hour
    where station_number = {bike_station_num} AND 
    order by time_queried desc, last_update
    limit 1;"""
    sql_query(statement)
    df_future = pd.read_sql_query(statement, engine)
    categorical_columns = df_future[[
        'dayquery', 'hourquery', 'weather_main', 'dayquery', 'hourquery']].columns
    # Convert data type to category for these columns
    for column in categorical_columns:
        df_future[column] = df_future[column].astype('category')

    df_future["humidity"] = df_future["humidity"].fillna(0)
    df_final_future = pd.get_dummies(df_future, drop_first=False)
    for col in features:
        if col not in df_final_future.columns:
            df_final_future[col] = [0 for i in range(len(df_final_future))]
    result = model.predict(df_final_future[features])
    dictionary = dict(
        zip(df_final_future["last_update"].astype(str).to_list(), result.tolist()))
    connection.close()
    engine.dispose()
    return jsonify(dictionary)


@app.route("/hour48-<int:number>")
def hour48(number):
    model = joblib.load(f'../data_analytics/pickles/station-{number}.pkl')

    features = ['temp', 'humidity', 'wind_speed', 'pressure', 'dayquery_Friday', 'dayquery_Monday', 'dayquery_Saturday', 'dayquery_Sunday', 'dayquery_Thursday', 'dayquery_Tuesday', 'dayquery_Wednesday', 'weather_main_Clear', 'weather_main_Clouds', 'weather_main_Drizzle', 'weather_main_Fog', 'weather_main_Mist', 'weather_main_Rain', 'weather_main_Snow', 'weather_main_Thunderstorm',
                'hourquery_0', 'hourquery_1', 'hourquery_2', 'hourquery_3', 'hourquery_4', 'hourquery_5', 'hourquery_6', 'hourquery_7', 'hourquery_8', 'hourquery_9', 'hourquery_10', 'hourquery_11', 'hourquery_12', 'hourquery_13', 'hourquery_14', 'hourquery_15', 'hourquery_16', 'hourquery_17', 'hourquery_18', 'hourquery_19', 'hourquery_20', 'hourquery_21', 'hourquery_22', 'hourquery_23']

    print(len(features))
    # importance = model.feature_importances_
    # print(importance)
    # for i, v in enumerate(importance):
    #     print(f'Feature: {features[i]}, Score: {v:.5f}')

    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_URL = os.environ.get("DB_URL")

    engine = create_engine(
        "mysql+pymysql://{0}:{1}@{2}".format(DB_USER, DB_PASS, DB_URL), echo=True)
    connection = engine.connect()

    statement = f"""SELECT last_update, dayname(last_update) as dayquery, hour(last_update) as hourquery, temp, humidity, pressure, wind_speed, weather_main FROM dublin_bikes.weather_forecast_1hour
    where station_number = {number}
    order by time_queried desc, last_update
    limit 48;"""
    df_future = pd.read_sql_query(statement, engine)
    categorical_columns = df_future[[
        'dayquery', 'hourquery', 'weather_main', 'dayquery', 'hourquery']].columns
    # Convert data type to category for these columns
    for column in categorical_columns:
        df_future[column] = df_future[column].astype('category')

    df_future["humidity"] = df_future["humidity"].fillna(0)
    df_final_future = pd.get_dummies(df_future, drop_first=False)
    for col in features:
        if col not in df_final_future.columns:
            df_final_future[col] = [0 for i in range(len(df_final_future))]
    print(df_final_future.columns)
    print(len(df_final_future.columns))

    result = model.predict(df_final_future[features])
    dictionary = dict(
        zip(df_final_future["last_update"].astype(str).to_list(), result.tolist()))
    connection.close()
    engine.dispose()
    return jsonify(dictionary)


@app.route("/statstation-<int:number>")
def statstation(number):
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_URL = os.environ.get("DB_URL")

    engine = create_engine(
        "mysql+pymysql://{0}:{1}@{2}/dublin_bikes".format(DB_USER, DB_PASS, DB_URL), echo=True)
    connection = engine.connect()

    sql_create_schema = f"""SELECT * FROM dublin_bikes.availability
where number = {number} && abs(timestampdiff(day, now(), time_queried)) <= 7
order by time_queried asc;"""
    rows = engine.execute(sql_create_schema)  # execute select statement

    stations = []
    for row in rows:
        stations.append(dict(row))  # inset dict of data into list
        print(row)
    connection.close()
    engine.dispose()
    return jsonify(station=stations)  # return json string of data


@app.route("/averagestation-<int:number>")
def averagestation(number):
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_URL = os.environ.get("DB_URL")
    engine = create_engine(
        "mysql+pymysql://{0}:{1}@{2}/dublin_bikes".format(DB_USER, DB_PASS, DB_URL), echo=True)
    connection = engine.connect()
    sql_create_schema = f"""SELECT cast(avg(available_bikes) as char) as avgavailbikes, cast(avg(available_bike_stands) as char)as avgavailbikestation, Year(time_queried) as yearq, month(time_queried) as monthq, day(time_queried) as dateq FROM dublin_bikes.availability
where number = {number}
group by date(time_queried)
order by time_queried desc;"""

    rows = engine.execute(sql_create_schema)  # execute select statement
    connection.close()
    engine.dispose()
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
    global last_updated_availability_time, last_updated_availability_data, first_run
    if (((last_updated_availability_time - datetime.datetime.now()).total_seconds() < -900) or first_run):
        first_run = False
        sql_get_availability = """select db_a.number, position_lat, position_lng, name, address, available_bikes, available_bike_stands, max(db_a.last_update) as last_update
    FROM dublin_bikes.station db_s
    INNER JOIN dublin_bikes.availability db_a ON
    db_s.number = db_a.number
    GROUP BY number
    """  # create select statement for stations table
        print("INSIDE 1")
        rows = sql_query(sql_get_availability)  # execute select statement

        last_updated_availability_data = []
        for row in rows:
            last_updated_availability_data.append(
                dict(row))  # inset dict of data into list
            print(row)
        last_updated_availability_time = datetime.datetime.now()
    # return json string of data
    return jsonify(station=last_updated_availability_data)


@app.route("/current_weather")
def current_weather():
    """
    Get all stations
    render template to client
    """
    global last_updated_weather_time, last_updated_weather_data, first_run_weather
    if (((last_updated_weather_time - datetime.datetime.now())).total_seconds() < -900 or first_run_weather):
        first_run_weather = False
        sql_get_weather = """SELECT *
        FROM dublin_bikes.weather_current 
        ORDER  BY last_update DESC
        LIMIT  1;
            """
        print("INSIDE 2")

        rows = sql_query(sql_get_weather)
        last_updated_weather_data = []
        for row in rows:
            # inset dict of data into list
            last_updated_weather_data.append(dict(row))
            print(row)
        last_updated_weather_time = datetime.datetime.now()
    # return json string of data
    return jsonify(weather=last_updated_weather_data)


if __name__ == "__main__":
    # default port is 5000 if you don't specify
    app.run(host="0.0.0.0", port=5000)
