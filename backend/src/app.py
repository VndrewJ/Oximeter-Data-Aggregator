from flask import Flask, jsonify
from flask_cors import CORS
from collections import deque
import csv
import os
import time
import threading
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow React frontend

# Ring buffer to store last N readings
BUFFER_SIZE = 50
buffer = deque(maxlen=BUFFER_SIZE)

# CSV file path
csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "health_data.csv")
csv_path = os.path.abspath(csv_path)

def load_initial_data():
    """Load existing CSV data into the buffer."""
    try:
        with open(csv_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                buffer.append(row)
    except FileNotFoundError:
        print(f"CSV file not found at {csv_path}")

load_initial_data()

@app.route("/data")
def get_data():
    """Return the most recent readings as JSON."""
    return jsonify(list(buffer))

@app.route("/")
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "Flask backend running", "buffer_size": len(buffer)})

# --- SocketIO events ---
@socketio.on("connect")
def handle_connect():
    print("Client connected")
    emit("vitals", list(buffer))  # send current buffer on connect

def watch_csv():
    """
    Continuously watches the CSV file for new lines and pushes updates to clients.
    """
    last_index = len(buffer)  # start after existing lines
    while True:
        try:
            with open(csv_path, newline="") as csvfile:
                reader = list(csv.DictReader(csvfile))
                # Push only new rows
                for row in reader[last_index:]:
                    buffer.append(row)
                    socketio.emit("vitals", list(buffer))
                last_index = len(reader)
        except FileNotFoundError:
            print(f"CSV file not found at {csv_path}")
        time.sleep(1)  # check for new data every second

# Start the CSV watching thread
threading.Thread(target=watch_csv, daemon=True).start()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
