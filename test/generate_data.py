# simulator.py
import csv
import random
import time
import os

# Set the path to backend/data/oximeter_test_data.csv
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "backend", "data")
os.makedirs(DATA_DIR, exist_ok=True)
CSV_FILE = os.path.join(DATA_DIR, "oximeter_test_data.csv")

# Initialize CSV with headers (clears the file)
with open(CSV_FILE, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["timestamp", "spo2", "pulse"])

# Keep writing fake data every second
while True:
    row = [time.time(), random.randint(90, 100), random.randint(60, 100)]
    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(row)
    print("Wrote:", row)
    time.sleep(1)  #
