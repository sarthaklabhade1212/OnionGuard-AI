import csv
import time
import requests
import os
from datetime import datetime

SERVER = "http://localhost:5000/api/data"  # Change if server IP differs

DATA_CSV = os.path.join("data", "sensor_data.csv")

def read_samples():
    samples = []
    if not os.path.exists(DATA_CSV):
        print("No sample CSV found at", DATA_CSV)
        return samples
    with open(DATA_CSV, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                t = float(row["temperature"])
                h = float(row["humidity"])
                g = float(row["gas"])
                timestamp = row.get("timestamp") or datetime.utcnow().isoformat()
                samples.append({"temperature": t, "humidity": h, "gas": g, "timestamp": timestamp})
            except Exception:
                continue
    return samples

def send_sample(sample):
    try:
        res = requests.post(SERVER, json=sample, timeout=5)
        print("POST", res.status_code, res.text)
    except Exception as e:
        print("Error sending:", e)

def run_loop(delay=5):
    samples = read_samples()
    if not samples:
        print("No samples to send. Add rows to data/sensor_data.csv (beside header).")
        return
    i = 0
    while True:
        sample = samples[i % len(samples)]
        # update timestamp to now
        sample["timestamp"] = datetime.utcnow().isoformat()
        send_sample(sample)
        i += 1
        time.sleep(delay)

if __name__ == "__main__":
    # default sends one reading every 5 seconds (matches dashboard refresh)
    run_loop(delay=5)
