import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

DATA_FILE = os.path.join("data", "sensor_data.csv")
MODEL_FILE = os.path.join("model", "model.pkl")

os.makedirs("model", exist_ok=True)

def load_and_label(df):
    # Heuristic labeling — adjust with real labeled data later
    def label_row(row):
        h = row["humidity"]
        t = row["temperature"]
        g = row["gas"]
        score = 0
        if h > 75: score += 1
        if t > 28: score += 1
        if g > 400: score += 1
        return 1 if score >= 2 else 0

    df["label"] = df.apply(label_row, axis=1)
    return df

def train():
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found: {DATA_FILE}")
        return

    df = pd.read_csv(DATA_FILE)
    df = df.dropna(subset=["temperature", "humidity", "gas"])
    df = load_and_label(df)

    X = df[["temperature", "humidity", "gas"]].values
    y = df["label"].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print(classification_report(y_test, preds))

    joblib.dump(model, MODEL_FILE)
    print(f"Saved model to {MODEL_FILE}")

if __name__ == "__main__":
    train()
