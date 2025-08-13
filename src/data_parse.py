from flask import Flask, jsonify
from markupsafe import escape
import csv

app = Flask(__name__)  # <-- Add this line

@app.route("/<name>")
def hello(name):
    return f"Hello, {escape(name)}!"