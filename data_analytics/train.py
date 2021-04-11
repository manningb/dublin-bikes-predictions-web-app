import os
from csv import DictWriter

from sqlalchemy import create_engine
import api_keys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
from pandas import read_csv, to_datetime
from time import time
import joblib
import json
import multiprocessing
global weather_data

def get_weather_data():
    global weather_data
    DB_USER = api_keys.DB_USER
    DB_PASS = api_keys.DB_PASS
    DB_URL = api_keys.DB_URL

    engine = create_engine("mysql+pymysql://{0}:{1}@{2}".format(DB_USER, DB_PASS, DB_URL), echo=True)
    connection = engine.connect()

    statement_weather = """
    SELECT DISTINCT(last_update) as last_update, temp,wind_speed,pressure,humidity,weather_main 
    FROM dublin_bikes.weather_historical_daily
    UNION ALL
    SELECT DISTINCT(last_update) as last_update, temp,wind_speed,pressure,humidity,weather_main 
    FROM dublin_bikes.weather_current
    ;
    """

    df_weather = pd.read_sql_query(statement_weather, engine) # https://stackoverflow.com/questions/29525808/sqlalchemy-orm-conversion-to-pandas-dataframe
    connection.close()
    df_weather = df_weather[df_weather.last_update != '0000-00-00 00:00:00']
    threshold = 5
    threshold_ns = threshold * 60 * 1e9
    df_weather['last_update'] = to_datetime(np.round(df_weather.last_update.astype(np.int64) / threshold_ns) * threshold_ns)
    df_weather['last_update'] = pd.to_datetime(df_weather['last_update'])
    df_weather = df_weather.drop_duplicates()
    weather_data = df_weather

def get_data(station_number, weather_data):
    DB_USER = api_keys.DB_USER
    DB_PASS = api_keys.DB_PASS
    DB_URL = api_keys.DB_URL

    engine = create_engine("mysql+pymysql://{0}:{1}@{2}".format(DB_USER, DB_PASS, DB_URL), echo=True) 
    connection = engine.connect()

    statement_availability = f"""SELECT DISTINCT(availability.last_update) as last_update, dayname(availability.last_update) as dayquery, hour(availability.last_update) as hourquery, availability.available_bikes as available_bikes
    FROM dublin_bikes.availability
    where availability.number = {station_number}
    UNION ALL
    SELECT DISTINCT(historical_availability.last_update) as last_update, dayname(historical_availability.last_update) as dayquery, hour(historical_availability.last_update) as hourquery, historical_availability.available_bikes as available_bikes
    FROM dublin_bikes.historical_availability
    where historical_availability.number = {station_number}
    """

    df_availability = pd.read_sql_query(statement_availability, engine) # https://stackoverflow.com/questions/29525808/sqlalchemy-orm-conversion-to-pandas-dataframe
    connection.close()
    df_availability = df_availability[df_availability.last_update != '0000-00-00 00:00:00']
    df_availability['last_update'] = pd.to_datetime(df_availability['last_update'])

    threshold = 5
    threshold_ns = threshold * 60 * 1e9

    # compute "interval" to which each session belongs
    df_availability['last_update'] = to_datetime(np.round(df_availability.last_update.astype(np.int64) / threshold_ns) * threshold_ns)

    # join
    cols = ['last_update']
    df_availability = df_availability.drop_duplicates()
    joined_df = df_availability.merge(weather_data, on=cols, how='inner')
    return joined_df

# the following code is based on code presented in module COMP47350 lab 7
def printMetrics(testActualVal, predictions):
    #classification evaluation measures
    print('\n==============================================================================')
    print("MAE: ", metrics.mean_absolute_error(testActualVal, predictions))
    #print("accuracy score:", metrics.accuracy_score(testActualVal, predictions))
    #print("MSE: ", metrics.mean_squared_error(testActualVal, predictions))
    print("RMSE: ", metrics.mean_squared_error(testActualVal, predictions)**0.5)
    print("R2: ", metrics.r2_score(testActualVal, predictions))
    return {"MAE":metrics.mean_absolute_error(testActualVal, predictions), "RMSE":metrics.mean_squared_error(testActualVal, predictions)**0.5, "R2":metrics.r2_score(testActualVal, predictions)}

def get_pickle(df, number):
    categorical_columns = df[['dayquery', 'hourquery', 'weather_main', 'dayquery', 'hourquery']].columns
    # Convert data type to category for these columns
    for column in categorical_columns:
        df[column] = df[column].astype('category')

    continuous_columns = df.select_dtypes(['int64']).columns
    datetime_columns = df.select_dtypes(['datetime64[ns]']).columns
    df["humidity"] = df["humidity"].fillna(0)
    # the following code is based on code presented in module COMP47350 lab 7
    weather_dummies = pd.get_dummies(df['weather_main'], prefix='weather_main', drop_first=False)
    day_dummies = pd.get_dummies(df['dayquery'], prefix='dayquery', drop_first=False)
    hour_dummies = pd.get_dummies(df['hourquery'], prefix='hourquery', drop_first=False)
    all_features = ['temp', 'humidity', 'wind_speed', 'pressure', 'dayquery_Friday', 'dayquery_Monday', 'dayquery_Saturday', 'dayquery_Sunday', 'dayquery_Thursday', 'dayquery_Tuesday', 'dayquery_Wednesday', 'weather_main_Clear', 'weather_main_Clouds', 'weather_main_Drizzle', 'weather_main_Fog', 'weather_main_Mist', 'weather_main_Rain', 'weather_main_Snow', 'weather_main_Thunderstorm', 'hourquery_0', 'hourquery_1', 'hourquery_2', 'hourquery_3', 'hourquery_4', 'hourquery_5', 'hourquery_6', 'hourquery_7', 'hourquery_8', 'hourquery_9', 'hourquery_10', 'hourquery_11', 'hourquery_12', 'hourquery_13', 'hourquery_14', 'hourquery_15', 'hourquery_16', 'hourquery_17', 'hourquery_18', 'hourquery_19', 'hourquery_20', 'hourquery_21', 'hourquery_22', 'hourquery_23']

    # the following code is based on code presented in module COMP47350 lab 7
    df_final = pd.get_dummies(df, drop_first=False)
    df_final = df_final.drop(['last_update'], axis=1)
    for col in all_features:
        if col not in df_final.columns:
            df_final[col] = [0 for i in range(len(df_final))]

    # the following code is based on code presented in module COMP47350 lab 7
    # cont_features = ['temp', "humidity", "wind_speed", "pressure"]
    # categ_features = day_dummies.columns.values.tolist() + weather_dummies.columns.values.tolist() + hour_dummies.columns.values.tolist()
    # features = cont_features + categ_features
    # print(features)
    # print(len(features))
    X = df_final[all_features]
    y = df_final.available_bikes
    # the following code is based on code presented in module COMP47350 lab 7
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
    # the following code is based on code presented in module COMP47350 lab 7
    linreg = DecisionTreeRegressor().fit(X, y)
    linreg_predictions = linreg.predict(X[all_features])
    metrics = printMetrics(y, linreg_predictions)
    metrics["number"] = number
    with open('pickles/metrics.csv', 'a') as f_object:
        # Pass the file object and a list
        # of column names to DictWriter()
        # You will get a object of DictWriter
        dictwriter_object = DictWriter(f_object, fieldnames=list(metrics.keys()))

        # Pass the dictionary as an argument to the Writerow()
        dictwriter_object.writerow(metrics)

        # Close the file object
        f_object.close()

    joblib.dump(linreg, f'pickles/station-{number}.pkl')

def get_data_then_pickle(input):
    df = get_data(input[0], input[1])
    get_pickle(df, input[0])

# code taken from COMP30660 material
def pool_process(f, data, pool_size = multiprocessing.cpu_count()):
    if __name__ == '__main__':
        with multiprocessing.get_context('spawn').Pool(processes=pool_size) as pool:
            # tp1 = time.time()
            print(data, pool_size)
            result = pool.map(f, data)       # map f to the data using the Pool of processes to do the work
            pool.close() # No more processes
            pool.join()  # Wait for the pool processing to complete.
            # print("Results", result)
            # print("Overall Time:", int(time.time()-tp1))

def main():
    with open('static_bikes.json') as f:
      static_stations = json.load(f)

    # run this function once to get the weather data dataframe
    # stored in global var and used in get_data func
    get_weather_data()
    while (True):
        stations_pool = []
        for station in static_stations:
            if not os.path.exists(f"pickles/station-{station['number']}.pkl"):
                stations_pool.append([station['number'], weather_data])
                if len(stations_pool) == 4:
                    pool_process(get_data_then_pickle, stations_pool)
                    stations_pool = []
        break

if __name__ == "__main__":
    main()