
import unittest
import pytest

# First party modules
from app import app as runapp

# the following comes from https://medium.com/analytics-vidhya/how-to-test-flask-applications-aef12ae5181c
@pytest.fixture
def client():
    app = runapp
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_page_200_1(client):
    """
    Test the / returns status 200 when connected
    """
    rv = client.get("/")
    assert rv.status_code == 200

def test_page_200_2(client):
    """
        Test the /stationstats-2 returns status 200 when connected
    """
    rv = client.get("/stationstats-2")
    assert rv.status_code == 200

def test_page_200_3(client):
    """
        Test the /stations returns status 200 when connected
    """
    rv = client.get("/stations")
    assert rv.status_code == 200

def test_page_200_4(client):
    """
        Test the /statstation-2 returns status 200 when connected
    """
    rv = client.get("/statstation-2")
    assert rv.status_code == 200

def test_page_200_5(client):
    """
        Test the /averagestation-2 returns status 200 when connected
    """
    rv = client.get("/averagestation-2")
    assert rv.status_code == 200

def test_page_200_6(client):
    """
        Test the /hour48-2 returns status 200 when connected
    """
    rv = client.get("/hour48-2")
    assert rv.status_code == 200

def test_page_200_7(client):
    """
        Test the /current_weather returns status 200 when connected
    """
    rv = client.get("/current_weather")
    assert rv.status_code == 200

def test_data_48(client):
    """
    Test length of json output
    """
    rv = client.get("/hour48-2")
    assert len(rv.json) == 48

def test_data_48_json(client):
    """
    Test predicted values for model in appropriate range
    """
    rv = client.get("/hour48-2")
    for key in rv.json.keys():
        assert rv.json[key] >= 0 and rv.json[key] <= 40

def test_current_weather(client):
    """
    test length of json output
    """
    rv = client.get("/current_weather")
    assert len(rv.json) == 1

def test_current_weather(client):
    """
    test values returned for weather positive
    """
    rv = client.get("/current_weather")
    for key in  rv.json.keys():
        for weaetherkey in rv.json[key][0].keys():
            deskey = rv.json[key][0][weaetherkey]
            print("weatherkey", weaetherkey)
            print("deskey", deskey)
            if weaetherkey in ['feels_like', 'pressure', 'station_number', 'temp']:
                assert deskey > 0

def test_averagestation(client):
    """
    test average station values positive
    """
    rv = client.get("/averagestation-2")
    for station in rv.json:
        for key in station.keys():
            print(rv.json[0][key])
            assert float(rv.json[0][key]) > 0

def test_statstation(client):
    """
    test that the station stats returned are in the correct ranges and station is in the correct range
    """
    rv = client.get("/statstation-2")
    for station in rv.json['station']:
        print(station['available_bike_stands'])
        print(station['available_bikes'])
        print(station['number'])
        assert int(station['available_bike_stands']) >= 0 and int(station['available_bike_stands']) <= 40
        assert int(station['available_bikes']) >= 0 and int(station['available_bikes']) <= 40
        assert int(station['number']) >= 2 and int(station['number']) <= 117

if __name__ == '__main__':
    unittest.main(argv=['ignored', '-v'], exit=False)