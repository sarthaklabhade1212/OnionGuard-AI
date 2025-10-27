import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import pandas as pd
from datetime import datetime
from model.spoilage_predictor import SpoilagePredictor

DATA_FILE = os.path.join("data", "sensor_data.csv")
MODEL_FILE = os.path.join("model", "model.pkl")

app = Flask(__name__)
CORS(app)

# Ensure directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("model", exist_ok=True)

# Initialize data file with headers if missing
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["timestamp", "temperature", "humidity", "gas"])
    df.to_csv(DATA_FILE, index=False)

# Initialize predictor
predictor = SpoilagePredictor(model_path=MODEL_FILE)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data", methods=["POST"])
def receive_data():
    """
    Endpoint for ESP32 or simulators to post sensor readings.
    Expects JSON: { "temperature": float, "humidity": float, "gas": float, "timestamp": optional }
    """
    try:
        payload = request.get_json(force=True)
        temperature = float(payload.get("temperature"))
        humidity = float(payload.get("humidity"))
        gas = float(payload.get("gas"))
        timestamp = payload.get("timestamp") or datetime.utcnow().isoformat()

        # Append to CSV
        df_new = pd.DataFrame([{
            "timestamp": timestamp,
            "temperature": temperature,
            "humidity": humidity,
            "gas": gas
        }])
        df_new.to_csv(DATA_FILE, mode="a", header=False, index=False)

        # Make prediction
        pred = predictor.predict_single(temperature, humidity, gas)
        # Return a friendly flattened response
        response = {
            "status": "success",
            "data": {
                "temperature": temperature,
                "humidity": humidity,
                "gas": gas,
                "timestamp": timestamp,
                "prediction": pred
            }
        }
        return jsonify(response), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/latest", methods=["GET"])
def latest():
    try:
        df = pd.read_csv(DATA_FILE)
        if df.empty:
            return jsonify({"status": "empty"}), 200
        last = df.iloc[-1].to_dict()
        pred = predictor.predict_single(last["temperature"], last["humidity"], last["gas"])
        last["prediction"] = pred
        return jsonify({"status": "success", "data": last}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/history", methods=["GET"])
def history():
    try:
        df = pd.read_csv(DATA_FILE)
        df = df.tail(500)  # limit to last 500 rows for performance
        data = df.to_dict(orient="records")
        return jsonify({"status": "success", "data": data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    # Development: host 0.0.0.0 to be reachable by ESP32 on LAN
    app.run(host="0.0.0.0", port=5000, debug=True)
