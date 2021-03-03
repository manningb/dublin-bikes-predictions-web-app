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
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(app.static_folder, "static_bikes.json")
    print(json_url)
    with open(json_url, 'r') as f:
        return jsonify(json.load(f))

if __name__ == "__main__":
    #default port is 5000 if you don't specify
    app.run(debug=True, port=5000)