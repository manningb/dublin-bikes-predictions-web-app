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
    GMAP_API = ""
    return render_template("index.html", GMAP_API=GMAP_API)

@app.route("/static_bikes")
def static_bikes():
    """
    Get all stations
    render template to client
    """
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_URL = os.environ.get("DB_URL")

    engine = create_engine("mysql+pymysql://{0}:{1}@{2}".format(DB_USER, DB_PASS, DB_URL), echo=True) 
    connection = engine.connect()

    sql_create_schema = """SELECT * FROM `dublin_bikes`.`station`;""" # create select statement for stations table

    rows = engine.execute(sql_create_schema) # execute select statement

    stations = [] 
    for row in rows:
        stations.append(dict(row)) # inset dict of data into list
    return jsonify(station=stations) # return json string of data



if __name__ == "__main__":
    #default port is 5000 if you don't specify
    app.run(debug=True, port=5000)