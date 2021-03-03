from flask import Flask, render_template, jsonify
import json
import os
from sqlalchemy import create_engine
import os
import requests
import json

app = Flask("__name__", template_folder="templates")

@app.route("/")
def hello():
    GMAP_API = ""
    return render_template("index.html", GMAP_API=GMAP_API)

@app.route("/about")
def about():
    GMAP_API = os.environ.get("GMAP_API")
    return GMAP_API

@app.route("/contact")
def contact():
    return render_template("contact.html", title="Contact", heading="Contact Page")

@app.route("/output.json")
def output():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(app.static_folder, "output.json")
    print(json_url)
    with open(json_url, 'r') as f:
        return jsonify(json.load(f))

if __name__ == "__main__":
    #default port is 5000 if you don't specify
    app.run(debug=True, port=5000)