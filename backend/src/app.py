from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_cors import CORS
from markupsafe import escape
from collections import deque
import csv
import os

app = Flask(__name__) 
CORS(app) 

@app.route("/")
def home_page():
    return render_template("index.html")

@app.route("/data")
def get_data():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "oximeter_test_data.csv")
    csv_path = os.path.abspath(csv_path)
    
    buffer = deque(maxlen=20)  # ring buffer, max 20 readings
    
    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            buffer.append(row)  # only last 20 kept automatically
    
    return jsonify(list(buffer))

