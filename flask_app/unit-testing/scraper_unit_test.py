import os
import requests
import unittest
import pytest

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_URL = os.environ.get("DB_URL")
DB_PORT = os.environ.get("DB_PORT")
WEATHERKEY = os.environ.get("WEATHERKEY")
station_lat =53.3498
station_lat =6.2603
# API Key for Dublin Bikes JCDecaux & Other Variables for API
DubBike_API = os.environ.get("API_DubBike")
DubBike_NAME = "Dublin"
DubBike_STATIONS = "https://api.jcdecaux.com/vls/v1/stations/"


def test_JCDecaux():
    """
    testing the JCDeceaux api to ensure that it is working
    """
    r = requests.get(DubBike_STATIONS, params={"apiKey": DubBike_API, "contract": DubBike_NAME})
    assert r.status_code == 200

def test_JCDecaux_json():
    """
    testing the JCDeceaux json to ensure that it has been returned
    """
    r = requests.get(DubBike_STATIONS, params={"apiKey": DubBike_API, "contract": DubBike_NAME})
    assert len(r.json()) > 0

def test_weather():
    """
    testing the weather maps api to ensure working
    """
    r = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat={station_lat}&lon={station_lat}&appid={WEATHERKEY}")
    assert r.status_code == 200

def test_weather_json():
    """
    testing the weather maps api to ensure data has been returned
    """
    r = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat={station_lat}&lon={station_lat}&appid={WEATHERKEY}")
    assert len(r.json()) > 0

if __name__ == '__main__':
    unittest.main(argv=['ignored', '-v'], exit=False)
