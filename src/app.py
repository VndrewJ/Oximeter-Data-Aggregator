from flask import Flask, jsonify, render_template, request, redirect, url_for
from markupsafe import escape
import csv

app = Flask(__name__)  # <-- Add this line

@app.route("/")
def welcome():
    return render_template("index.html")
    

