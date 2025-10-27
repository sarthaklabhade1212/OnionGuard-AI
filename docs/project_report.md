# OnionGuard AI — Project Report

## Objective
Reduce post-harvest onion losses by using a smart, AI-enabled storage unit that monitors environment and predicts spoilage risk.

## Solution
An ESP32 collects temp/humidity/gas sensor data and sends it to a Flask server. The server stores data and runs a machine-learning model (or rule-based fallback) to predict spoilage risk. Farmers receive alerts via a web dashboard and voice notifications. The dashboard shows live readings and history.

## Hardware
- ESP32
- DHT11 (temperature/humidity)
- MQ-135 (air/gas)
- Optional: RTC module, SD card for local logs, solar/battery for power

## Software
- Flask backend (API + dashboard)
- Python ML stack (scikit-learn)
- Arduino code for ESP32

## Future work
- Calibrate MQ-135 and map to PPM values
- Add SMS/WhatsApp alerts (Twilio/WhatsApp API)
- Add multilingual (Marathi) voice messages and IVR integration
- Pilot deployment with Krishi Kendras
