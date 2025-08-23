from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_cors import CORS
from markupsafe import escape
import csv
import os

app = Flask(__name__) 
CORS(app) 

@app.route("/")
def home_page():
    return render_template("index.html")
    
@app.route("/data")
def get_data():
    data = []
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "oximeter_test_data.csv")
    csv_path = os.path.abspath(csv_path)
    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return jsonify(data)

