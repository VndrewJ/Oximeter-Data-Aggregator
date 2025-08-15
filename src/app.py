from flask import Flask, jsonify, render_template, request, redirect, url_for
from markupsafe import escape
import csv
import os

app = Flask(__name__)  # <-- Add this line

@app.route("/")
def home_page():
    return render_template("index.html")
    
@app.route("/data")
def goto_data():
    data = []
    # Go up one directory from src, then into data
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "oximeter_test_data.csv")
    csv_path = os.path.abspath(csv_path)  # Get absolute path
    with open(csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return render_template("display_data.html", table_data=data)

